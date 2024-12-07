# farm/tasks.py (using Celery for background tasks)
from celery import shared_task
from .models import *
from datetime import datetime, timedelta
from django.db.models import Avg

@shared_task
def check_health_checkups():
    tomorrow = datetime.now().date() + timedelta(days=1)
    upcoming_checkups = HealthRecord.objects.filter(
        next_check_up=tomorrow
    ).select_related('cattle', 'cattle__owner')

    for record in upcoming_checkups:
        Notification.objects.create(
            user=record.cattle.owner,
            title=f"Health Check-up Due Tomorrow",
            message=f"Health check-up due tomorrow for {record.cattle.name}",
            priority='high',
            related_url=f'/farm/cattle/{record.cattle.id}/'
        )

@shared_task
def check_milk_production_anomalies():
    yesterday = datetime.now().date() - timedelta(days=1)
    productions = MilkProduction.objects.filter(
        date=yesterday
    ).select_related('cattle', 'cattle__owner')

    for prod in productions:
        # Calculate the average production for the same cattle on previous days
        avg_result = MilkProduction.objects.filter(
            cattle=prod.cattle,
            date__lt=yesterday
        ).aggregate(
            avg_morning=Avg('morning_amount'),
            avg_evening=Avg('evening_amount')
        )

        # Sum the averages of morning and evening amounts
        avg_production = (avg_result['avg_morning'] or 0) + (avg_result['avg_evening'] or 0)

        if avg_production > 0 and prod.total_amount < (avg_production * 0.7):  # 30% decrease
            Notification.objects.create(
                user=prod.cattle.owner,
                title="Low Milk Production Alert",
                message=f"Significant decrease in milk production for {prod.cattle.name}",
                priority='high',
                related_url=f'/farm/cattle/{prod.cattle.id}/'
            )

# farm/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
import datetime
from django.db.models import Sum, Avg
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime, timedelta
import csv
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Cattle, MilkProduction, HealthRecord
from .forms import CattleForm, MilkProductionForm, HealthRecordForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


# Add the new logout view
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        if 'password_change' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('farm:profile')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            # Handle profile update
            user = request.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('farm:profile')

    password_form = PasswordChangeForm(request.user)
    return render(request, 'farm/profile.html', {
        'password_form': password_form,
    })


@login_required
def dashboard(request):
    total_cattle = Cattle.objects.filter(owner=request.user, status='active').count()
    today_milk = MilkProduction.objects.filter(
        recorded_by=request.user,
        date=datetime.date.today()
    ).aggregate(
        total=Sum('morning_amount') + Sum('evening_amount')
    )['total'] or 0
    
    recent_health_records = HealthRecord.objects.filter(
        recorded_by=request.user
    ).order_by('-date')[:5]
    
    context = {
        'total_cattle': total_cattle,
        'today_milk': today_milk,
        'recent_health_records': recent_health_records,
    }
    return render(request, 'farm/dashboard.html', context)

# Cattle Views
@login_required
def cattle_list(request):
    cattle = Cattle.objects.filter(owner=request.user).order_by('-created_at')
    paginator = Paginator(cattle, 10)
    page = request.GET.get('page')
    cattle = paginator.get_page(page)
    return render(request, 'farm/cattle_list.html', {'cattle': cattle})

@login_required
def cattle_detail(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk, owner=request.user)
    milk_records = MilkProduction.objects.filter(cattle=cattle).order_by('-date')[:10]
    health_records = HealthRecord.objects.filter(cattle=cattle).order_by('-date')[:10]
    context = {
        'cattle': cattle,
        'milk_records': milk_records,
        'health_records': health_records,
    }
    return render(request, 'farm/cattle_detail.html', context)

@login_required
def cattle_add(request):
    if request.method == 'POST':
        form = CattleForm(request.POST)
        if form.is_valid():
            cattle = form.save(commit=False)
            cattle.owner = request.user
            cattle.save()
            messages.success(request, 'Cattle added successfully!')
            return redirect('cattle_detail', pk=cattle.pk)
    else:
        form = CattleForm()
    return render(request, 'farm/cattle_form.html', {'form': form, 'title': 'Add Cattle'})

# Milk Production Views
@login_required
def milk_production_list(request):
    productions = MilkProduction.objects.filter(
        recorded_by=request.user
    ).order_by('-date')
    paginator = Paginator(productions, 10)
    page = request.GET.get('page')
    productions = paginator.get_page(page)
    return render(request, 'farm/milk_production_list.html', {'productions': productions})

@login_required
def milk_production_add(request):
    if request.method == 'POST':
        form = MilkProductionForm(request.POST)
        if form.is_valid():
            production = form.save(commit=False)
            production.recorded_by = request.user
            production.save()
            messages.success(request, 'Milk production record added successfully!')
            return redirect('milk_production_list')
    else:
        form = MilkProductionForm()
    return render(request, 'farm/milk_production_form.html', {'form': form})

# Health Record Views
@login_required
def health_record_list(request):
    health_records = HealthRecord.objects.all()
    return render(request, 'farm/health_record_list.html', {'health_records': health_records})

@login_required
def health_record_add(request):
    if request.method == 'POST':
        form = HealthRecordForm(request.POST, request.FILES)
        if form.is_valid():
            health_record = form.save(commit=False)
            health_record.recorded_by = request.user
            health_record.save()
            messages.success(request, 'Health record added successfully.')
            return redirect('farm:health_record_list')  # Added 'farm:' namespace here
    else:
        form = HealthRecordForm()
    
    return render(request, 'farm/health_record_form.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthRecord
from .forms import HealthRecordForm

# ... your existing views ...

@login_required
def health_record_edit(request, pk):
    health_record = get_object_or_404(HealthRecord, pk=pk)
    if request.method == 'POST':
        form = HealthRecordForm(request.POST, request.FILES, instance=health_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Health record updated successfully.')
            return redirect('farm:health_record_list')
    else:
        form = HealthRecordForm(instance=health_record)
    return render(request, 'farm/health_record_form.html', {'form': form, 'edit_mode': True})

@login_required
def health_record_delete(request, pk):
    health_record = get_object_or_404(HealthRecord, pk=pk)
    if request.method == 'POST':
        health_record.delete()
        messages.success(request, 'Health record deleted successfully.')
        return redirect('farm:health_record_list')
    return render(request, 'farm/health_record_confirm_delete.html', {'health_record': health_record})


# farm/views.py
from django.db.models import Q

@login_required
def cattle_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    cattle = Cattle.objects.filter(owner=request.user)
    
    if search_query:
        cattle = cattle.filter(
            Q(tag_number__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    if status_filter:
        cattle = cattle.filter(status=status_filter)
    
    cattle = cattle.order_by('-created_at')
    
    paginator = Paginator(cattle, 10)
    page = request.GET.get('page')
    cattle = paginator.get_page(page)
    
    context = {
        'cattle': cattle,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'farm/cattle_list.html', context)




@login_required
def milk_production_list(request):
    # Get all milk production records
    milk_records = MilkProduction.objects.all().order_by('-date')

    # Calculate daily totals
    daily_totals = MilkProduction.objects.values('date').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-date')

    context = {
        'milk_records': milk_records,
        'daily_totals': daily_totals,
    }
    return render(request, 'farm/milk_production_list.html', context)

@login_required
def milk_production_export(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    productions = MilkProduction.objects.filter(recorded_by=request.user)
    if start_date:
        productions = productions.filter(date__gte=start_date)
    if end_date:
        productions = productions.filter(date__lte=end_date)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="milk_production.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Cattle', 'Morning Amount', 'Evening Amount', 'Total Amount'])
    
    for prod in productions:
        writer.writerow([
            prod.date,
            prod.cattle.name,
            prod.morning_amount,
            prod.evening_amount,
            prod.total_amount
        ])
    
    return response

# views.py

from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import TruncDate
from django.utils import timezone

def analytics_dashboard(request):
    # Get date range (default to last 30 days if not specified)
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=30)

    # Get milk production data
    milk_data = MilkProduction.objects.filter(
        date__range=[start_date, end_date]
    ).annotate(
        morning_amount=Case(
            When(milking_session='morning', then='quantity'),
            default=0,
            output_field=DecimalField(),
        ),
        afternoon_amount=Case(
            When(milking_session='afternoon', then='quantity'),
            default=0,
            output_field=DecimalField(),
        ),
        evening_amount=Case(
            When(milking_session='evening', then='quantity'),
            default=0,
            output_field=DecimalField(),
        )
    ).values('date').annotate(
        total_morning=Sum('morning_amount'),
        total_afternoon=Sum('afternoon_amount'),
        total_evening=Sum('evening_amount'),
        daily_total=Sum('quantity')
    ).order_by('date')

    # Calculate total production
    total_production = MilkProduction.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Calculate average daily production
    days_count = (end_date - start_date).days + 1
    avg_daily_production = total_production / days_count if days_count > 0 else 0

    # Get top producing cattle
    top_cattle = MilkProduction.objects.filter(
        date__range=[start_date, end_date]
    ).values(
        'cattle__name',
        'cattle__tag_number'
    ).annotate(
        total_production=Sum('quantity')
    ).order_by('-total_production')[:5]

    # Prepare data for charts
    dates = [entry['date'].strftime('%Y-%m-%d') for entry in milk_data]
    morning_data = [float(entry['total_morning'] or 0) for entry in milk_data]
    afternoon_data = [float(entry['total_afternoon'] or 0) for entry in milk_data]
    evening_data = [float(entry['total_evening'] or 0) for entry in milk_data]
    daily_totals = [float(entry['daily_total'] or 0) for entry in milk_data]

    context = {
        'total_production': total_production,
        'avg_daily_production': avg_daily_production,
        'top_cattle': top_cattle,
        'chart_data': {
            'dates': dates,
            'morning_data': morning_data,
            'afternoon_data': afternoon_data,
            'evening_data': evening_data,
            'daily_totals': daily_totals,
        },
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'farm/analytics_dashboard.html', context)


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from farm.utils import log_activity 
@login_required
def export_milk_production_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    cattle_id = request.GET.get('cattle')
    
    productions = MilkProduction.objects.filter(recorded_by=request.user)
    if start_date:
        productions = productions.filter(date__gte=start_date)
    if end_date:
        productions = productions.filter(date__lte=end_date)
    if cattle_id:
        productions = productions.filter(cattle_id=cattle_id)
    
    # Log the export activity
# farm/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notification
from django.contrib import messages

@login_required
def notifications_list(request):
    """
    Display list of notifications for the current user
    """
    # Get all notifications for the current user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate notifications
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    # Mark all unread notifications as read
    if request.GET.get('mark_all_read'):
        unread_notifications = Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        )
        for notification in unread_notifications:
            notification.mark_as_read()
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications_list')

    context = {
        'notifications': notifications,
        'unread_count': Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).count()
    }
    return render(request, 'farm/notifications_list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications_list')

@login_required
def delete_notification(request, notification_id):
    """
    Delete a specific notification
    """
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()
        messages.success(request, 'Notification deleted successfully.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
    return redirect('notifications_list')

# farm/views.py
@login_required
def mark_notification_read(request, notification_id):  # This is the correct name
    """
    Mark a specific notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications_list')

# farm/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import ActivityLog
from django.contrib.admin.views.decorators import staff_member_required


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import ActivityLog
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth import get_user_model


@login_required
def activity_log_list(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category = request.GET.get('category')

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    if category:
        logs = logs.filter(category=category)

    # Pagination
    paginator = Paginator(logs, 25)  # Show 25 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'logs': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'farm/activity_logs.html', context)

# farm/views.py
from django.contrib.auth.decorators import login_required

def cattle_add(request):
    # Your logic for adding cattle
    return render(request, 'farm/cattle_add.html')

@login_required
def create_cattle(request):
    if request.method == 'POST':
        form = CattleForm(request.POST)
        if form.is_valid():
            cattle = form.save(commit=False)
            cattle.owner = request.user
            cattle.save()
            return redirect('cattle_detail', pk=cattle.pk)
    else:
        form = CattleForm()
    return render(request, 'farm/cattle_form.html', {'form': form})

@login_required
def dashboard(request):
    # Filter cattle by the logged-in user
    cattle = Cattle.objects.filter(owner=request.user)
    context = {
        'cattle': cattle,
        # ... other context data ...
    }
    return render(request, 'farm/dashboard.html', context)

# farm/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from .models import Cattle
from .forms import CattleForm

@login_required
def cattle_edit(request, pk):
    # Get the cattle object or return 404 if not found
    cattle = get_object_or_404(Cattle, pk=pk)
    
    # Check if the user owns this cattle
    if cattle.owner != request.user:
        return HttpResponseForbidden("You don't have permission to edit this cattle.")
    
    if request.method == 'POST':
        form = CattleForm(request.POST, request.FILES, instance=cattle)
        if form.is_valid():
            # Save the form
            cattle = form.save(commit=False)
            cattle.owner = request.user
            cattle.save()
            
            # Add success message
            messages.success(request, f'Cattle {cattle.name} has been updated successfully.')
            
            # Redirect to cattle detail page
            return redirect('farm:cattle_detail', pk=cattle.pk)
    else:
        form = CattleForm(instance=cattle)
    
    context = {
        'form': form,
        'cattle': cattle,
        'title': f'Edit Cattle - {cattle.name}',
        'submit_text': 'Update Cattle'
    }
    
    return render(request, 'farm/edit.html', context)

@login_required
def cattle_delete(request, pk):
    # Get the cattle object or return 404 if not found
    cattle = get_object_or_404(Cattle, pk=pk)
    
    # Check if the user owns this cattle
    if cattle.owner != request.user:
        return HttpResponseForbidden("You don't have permission to delete this cattle.")
    
    if request.method == 'POST':
        # Store cattle name for success message
        cattle_name = cattle.name
        
        # Delete the cattle
        cattle.delete()
        
        # Add success message
        messages.success(request, f'Cattle {cattle_name} has been deleted successfully.')
        
        # Redirect to cattle list
        return redirect('farm:cattle_list')
    
    context = {
        'cattle': cattle,
        'title': f'Delete Cattle - {cattle.name}',
    }
    
    return render(request, 'farm/delete.html', context)

# farm/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CattleForm

@login_required
def cattle_add(request):
    if request.method == 'POST':
        form = CattleForm(request.POST, request.FILES)
        if form.is_valid():
            cattle = form.save(commit=False)
            cattle.owner = request.user
            cattle.save()
            messages.success(request, 'New cattle added successfully!')
            return redirect('farm:cattle_detail', pk=cattle.pk)
    else:
        form = CattleForm()
    
    context = {
        'form': form,
        'title': 'Add New Cattle'
    }
    return render(request, 'farm/add.html', context)

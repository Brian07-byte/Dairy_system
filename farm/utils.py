# farm/utils.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.db.models import Sum


def generate_milk_production_pdf(productions, title="Milk Production Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Heading1']))
    
    # Create table data
    data = [['Date', 'Cattle', 'Morning (L)', 'Evening (L)', 'Total (L)']]
    for prod in productions:
        data.append([
            prod.date.strftime('%Y-%m-%d'),
            prod.cattle.name,
            f"{prod.morning_amount:.2f}",
            f"{prod.evening_amount:.2f}",
            f"{prod.total_amount:.2f}"
        ])
    
    # Calculate totals
    totals = productions.aggregate(
        total_morning=Sum('morning_amount'),
        total_evening=Sum('evening_amount')
    )
    data.append([
        'TOTAL',
        '',
        f"{totals['total_morning']:.2f}",
        f"{totals['total_evening']:.2f}",
        f"{(totals['total_morning'] + totals['total_evening']):.2f}"
    ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


# farm/utils.py
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog

def log_activity(user, action, obj, description='', ip_address=None):
    """
    Log user activities in the system
    
    Args:
        user: The user performing the action
        action: String indicating the type of action ('create', 'update', 'delete', 'view', 'export')
        obj: The model instance being acted upon
        description: Optional description of the action
        ip_address: IP address of the user (optional)
    """
    content_type = ContentType.objects.get_for_model(obj)
    
    ActivityLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=obj.id,
        description=description,
        ip_address=ip_address
    )

def get_client_ip(request):
    """
    Get the client's IP address from the request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Add any other utility functions you might need
def calculate_milk_statistics(milk_records):
    """
    Calculate statistics from milk production records
    """
    if not milk_records:
        return {
            'total_yield': 0,
            'average_daily': 0,
            'highest_yield': 0,
            'lowest_yield': 0
        }
    
    total_yield = sum(record.total_yield for record in milk_records)
    average_daily = total_yield / len(milk_records)
    highest_yield = max(record.total_yield for record in milk_records)
    lowest_yield = min(record.total_yield for record in milk_records)
    
    return {
        'total_yield': total_yield,
        'average_daily': average_daily,
        'highest_yield': highest_yield,
        'lowest_yield': lowest_yield
    }

def format_date_range(start_date, end_date):
    """
    Format date range for reports and displays
    """
    if start_date == end_date:
        return start_date.strftime('%B %d, %Y')
    return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"

def validate_date_range(start_date, end_date):
    """
    Validate that the date range is valid
    """
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")
    return True

def generate_tag_number():
    """
    Generate a unique tag number for new cattle
    """
    from .models import Cattle
    import random
    import string
    
    while True:
        # Generate a random tag number
        tag = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # Check if it already exists
        if not Cattle.objects.filter(tag_number=tag).exists():
            return tag

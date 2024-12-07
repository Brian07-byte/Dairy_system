from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

from decimal import Decimal
from datetime import timedelta
from django.db.models import Sum

class Cattle(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('deceased', 'Deceased'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cattle',
        verbose_name='Owner'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Name'
    )
    tag_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Tag Number'
    )
    breed = models.CharField(
        max_length=100,
        verbose_name='Breed'
    )
    date_of_birth = models.DateField(
        verbose_name='Date of Birth'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name='Gender'
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Weight (kg)',
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )

    class Meta:
        verbose_name = 'Cattle'
        verbose_name_plural = 'Cattle'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tag_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.tag_number}"

    def age(self):
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
            today.month == self.date_of_birth.month and 
            today.day < self.date_of_birth.day
        ):
            age -= 1
        return age

    def get_total_milk_production(self):
        return MilkProduction.objects.filter(cattle=self).aggregate(
            total=Sum('quantity')
        )['total'] or Decimal('0.00')

    def get_average_daily_production(self, days=30):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        productions = MilkProduction.objects.filter(
            cattle=self,
            date__range=[start_date, end_date]
        )
        total = productions.aggregate(
            total=Sum('quantity')
        )['total'] or Decimal('0.00')
        return total / days if total else Decimal('0.00')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
class MilkProduction(models.Model):
    MILKING_SESSION_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening')
    ]

    cattle = models.ForeignKey(
        'Cattle',
        on_delete=models.CASCADE,
        related_name='milk_productions',
        verbose_name='Cattle'
    )
    date = models.DateField(
        verbose_name='Date'
    )
    milking_session = models.CharField(
        max_length=10,
        choices=MILKING_SESSION_CHOICES,
        verbose_name='Milking Session'
    )
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Quantity (L)'
    )
    fat_content = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Fat Content (%)'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='milk_productions',
        verbose_name='Recorded By'
    )

    class Meta:
        ordering = ['-date']
        unique_together = ['cattle', 'date', 'milking_session']
        verbose_name = 'Milk Production'
        verbose_name_plural = 'Milk Productions'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['cattle', 'date']),
        ]

    def __str__(self):
        return f"{self.cattle.name} - {self.date} {self.milking_session}"
    



class HealthRecord(models.Model):
    RECORD_TYPES = [
        ('vaccination', 'Vaccination'),
        ('treatment', 'Treatment'),
        ('check_up', 'Check-up'),
        ('deworming', 'Deworming'),
        ('insemination', 'Insemination'),
        ('pregnancy_check', 'Pregnancy Check'),
    ]

    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='health_records',
        verbose_name='Cattle'
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPES,
        verbose_name='Record Type'
    )
    date = models.DateField(
        verbose_name='Date'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    medicine = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Medicine'
    )
    dosage = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Dosage'
    )
    vet_name = models.CharField(
        max_length=100,
        verbose_name='Veterinarian Name'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Cost'
    )
    next_checkup_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Next Checkup Date'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Recorded By'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    attachment = models.FileField(
        upload_to='health_records/',
        null=True,
        blank=True,
        verbose_name='Attachment'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['next_checkup_date']),
            models.Index(fields=['record_type']),
        ]

    def __str__(self):
        return f"{self.cattle.name} - {self.record_type} - {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


        


class Breeding(models.Model):
    BREEDING_TYPE_CHOICES = [
        ('natural', 'Natural'),
        ('artificial', 'Artificial Insemination'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('unsuccessful', 'Unsuccessful'),
    ]

    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='breeding_records',
        verbose_name='Cattle'
    )
    breeding_type = models.CharField(
        max_length=20,
        choices=BREEDING_TYPE_CHOICES,
        verbose_name='Breeding Type'
    )
    date = models.DateField(
        verbose_name='Breeding Date'
    )
    sire_details = models.CharField(
        max_length=200,
        verbose_name='Sire Details'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    expected_calving_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Expected Calving Date'
    )
    actual_calving_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Actual Calving Date'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Cost'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Recorded By'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Breeding Record'
        verbose_name_plural = 'Breeding Records'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['expected_calving_date']),
        ]

    def __str__(self):
        return f"{self.cattle.name} - {self.breeding_type} - {self.date}"

class Feed(models.Model):
    FEED_TYPE_CHOICES = [
        ('forage', 'Forage'),
        ('concentrate', 'Concentrate'),
        ('supplement', 'Supplement'),
        ('mineral', 'Mineral'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Feed Name'
    )
    feed_type = models.CharField(
        max_length=20,
        choices=FEED_TYPE_CHOICES,
        verbose_name='Feed Type'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Quantity (kg)'
    )
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Cost per Unit'
    )
    purchase_date = models.DateField(
        verbose_name='Purchase Date'
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Expiry Date'
    )
    supplier = models.CharField(
        max_length=200,
        verbose_name='Supplier'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Recorded By'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Feed'
        verbose_name_plural = 'Feeds'
        indexes = [
            models.Index(fields=['feed_type']),
            models.Index(fields=['purchase_date']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.feed_type}"

    @property
    def total_cost(self):
        return self.quantity * self.cost_per_unit

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name='Action'
    )
    model_name = models.CharField(
        max_length=50,
        verbose_name='Model Name'
    )
    object_id = models.PositiveIntegerField(
        verbose_name='Object ID'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name} - {self.timestamp}"
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('health_checkup', 'Health Checkup Due'),
        ('vaccination', 'Vaccination Due'),
        ('breeding', 'Breeding Related'),
        ('feed_inventory', 'Feed Inventory Alert'),
        ('milk_production', 'Milk Production Alert'),
        ('general', 'General Notice'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    message = models.TextField(
        verbose_name='Message'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='Notification Type'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        verbose_name='Priority'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='User'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Read Status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Read At'
    )
    related_to = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Related Cattle'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.notification_type}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


# In models.py, update the ActivityLog model

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name='Action'
    )
    model_name = models.CharField(
        max_length=50,
        verbose_name='Model Name'
    )
    object_id = models.PositiveIntegerField(
        verbose_name='Object ID'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name} - {self.timestamp}"

    @classmethod
    def log_activity(cls, user, action, model_name, object_id, description, ip_address=None):
        """
        Class method to create an activity log entry
        """
        return cls.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            ip_address=ip_address
        )

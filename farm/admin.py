from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone

from .models import (
    Cattle, MilkProduction, HealthRecord,
    Breeding, Feed, ActivityLog, Notification
)

@admin.register(Cattle)
class CattleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag_number', 'breed', 'gender', 
                   'age', 'weight', 'status', 'total_milk_production')
    list_filter = ('status', 'gender', 'breed')
    search_fields = ('name', 'tag_number', 'breed')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'tag_number', 'breed', 'date_of_birth', 
                      'gender', 'weight', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    def total_milk_production(self, obj):
        return f"{obj.get_total_milk_production()} L"
    total_milk_production.short_description = 'Total Milk Production'

@admin.register(MilkProduction)
class MilkProductionAdmin(admin.ModelAdmin):
    list_display = ('cattle', 'date', 'milking_session', 
                   'quantity', 'fat_content', 'recorded_by')
    list_filter = ('milking_session', 'date', 'cattle')
    search_fields = ('cattle__name', 'cattle__tag_number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('cattle', 'recorded_by')

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('cattle', 'record_type', 'date', 
                   'vet_name', 'cost', 'next_checkup_date')
    list_filter = ('record_type', 'date', 'vet_name')
    search_fields = ('cattle__name', 'cattle__tag_number', 
                    'description', 'medicine')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('cattle', 'record_type', 'date', 'description')
        }),
        ('Medical Details', {
            'fields': ('medicine', 'dosage', 'vet_name', 'cost')
        }),
        ('Follow-up', {
            'fields': ('next_checkup_date', 'attachment')
        }),
        ('Record Information', {
            'fields': ('recorded_by', 'created_at')
        }),
    )

@admin.register(Breeding)
class BreedingAdmin(admin.ModelAdmin):
    list_display = ('cattle', 'breeding_type', 'date', 
                   'status', 'expected_calving_date', 'actual_calving_date')
    list_filter = ('breeding_type', 'status', 'date')
    search_fields = ('cattle__name', 'cattle__tag_number', 
                    'sire_details')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Breeding Information', {
            'fields': ('cattle', 'breeding_type', 'date', 
                      'sire_details', 'status')
        }),
        ('Calving Details', {
            'fields': ('expected_calving_date', 'actual_calving_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'cost', 'recorded_by', 'created_at')
        }),
    )

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'feed_type', 'quantity', 
                   'cost_per_unit', 'total_cost', 'purchase_date', 
                   'expiry_date')
    list_filter = ('feed_type', 'purchase_date', 'supplier')
    search_fields = ('name', 'supplier')
    readonly_fields = ('created_at', 'total_cost')
    date_hierarchy = 'purchase_date'

    fieldsets = (
        ('Feed Information', {
            'fields': ('name', 'feed_type', 'quantity', 
                      'cost_per_unit', 'total_cost')
        }),
        ('Purchase Details', {
            'fields': ('purchase_date', 'expiry_date', 'supplier')
        }),
        ('Additional Information', {
            'fields': ('notes', 'recorded_by', 'created_at')
        }),
    )

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 
                   'object_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'priority', 
                   'user', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 
                  'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at', 'read_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'message', 'notification_type', 
                      'priority')
        }),
        ('Status', {
            'fields': ('user', 'is_read', 'read_at', 'related_to')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new notifications
            obj.user = request.user
        super().save_model(request, obj, form, change)

# Register custom admin site header and title
admin.site.site_header = 'Dairy Farm Management System'
admin.site.site_title = 'Dairy Farm Admin'
admin.site.index_title = 'Farm Management'

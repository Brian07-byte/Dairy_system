# farm/urls.py
from django.urls import path
from . import views

app_name = 'farm'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    
    path('logout/', views.logout_view, name='logout'),  # Add this line
    
    
    # Cattle Management
    path('cattle/', views.cattle_list, name='cattle_list'),
    path('cattle/add/', views.cattle_add, name='cattle_create'),
    path('cattle/<int:pk>/', views.cattle_detail, name='cattle_detail'),
    path('cattle/<int:pk>/edit/', views.cattle_edit, name='cattle_edit'),
    path('cattle/<int:pk>/delete/', views.cattle_delete, name='cattle_delete'),
    
    
    # Milk Production
    path('milk/', views.milk_production_list, name='milk_production_list'),
    path('milk/add/', views.milk_production_add, name='milk_production_add'),
    path('milk/export/', views.milk_production_export, name='milk_production_export'),
    path('milk/export/pdf/', views.export_milk_production_pdf, name='milk_production_pdf'),
    
    # Health Records
    path('health/', views.health_record_list, name='health_record_list'),
    path('health/add/', views.health_record_add, name='health_record_add'),
    path('health/<int:pk>/edit/', views.health_record_edit, name='health_record_edit'),
    path('health/<int:pk>/delete/', views.health_record_delete, name='health_record_delete'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),  # Fixed name
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # Activity Logs
   path('logs/', views.activity_log_list, name='activity_log_list'),

    
]

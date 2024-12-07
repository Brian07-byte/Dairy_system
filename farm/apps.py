from django.apps import AppConfig

class FarmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'farm'
    label = 'farm_management'  # Add this line to make the label unique

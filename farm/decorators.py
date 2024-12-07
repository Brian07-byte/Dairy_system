# farm/decorators.py
from functools import wraps
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Administrator'
    MANAGER = 'manager', 'Farm Manager'
    WORKER = 'worker', 'Farm Worker'
    VIEWER = 'viewer', 'Viewer'

# CustomUser model should extend AbstractUser to include the `role` field
class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.WORKER
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator

# farm/models.py
class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Administrator'
    MANAGER = 'manager', 'Farm Manager'
    WORKER = 'worker', 'Farm Worker'
    VIEWER = 'viewer', 'Viewer'

# Update CustomUser model to include role
class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.WORKER
    )

# Example usage in views
@login_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def add_cattle(request):
    # Only admins and managers can add cattle
    ...

@login_required
@role_required([UserRole.ADMIN])
def delete_cattle(request, pk):
    # Only admins can delete cattle
    ...

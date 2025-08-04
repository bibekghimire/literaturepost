from django.db import models
from rest_framework.permissions import BasePermission

class RoleChoices(models.TextChoices):
    ADMIN= 'AD', 'Admin'
    STAFF= 'ST', 'Staff'
    CREATOR= 'CR', 'Creator'

class StatusChoices(models.TextChoices):
    ACTIVE='ACT', 'Active'
    SUSPENDED= 'SUS', 'Suspended'
    DELETED= 'DEL', 'Deleted'


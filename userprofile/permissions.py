from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class CanCreateManageUserProfile(BasePermission):
    """
    - Admins can manage STAFF and CREATORS, but not other ADMINS.
    - Staff can manage only CREATORS.
    - Creators cannot manage anyone.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        current_role=getattr(request.user,'role',None)
        target_role=getattr(obj,'role',None)
        if not current_role:
            return False
        if request.user==obj.user:
            return True
        if current_role=='AD':
            return target_role != 'AD'
        elif current_role=='ST':
            return target_role == 'CR'
        else:
            return False
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return request.user.role in ['AD','ST','CR']
        return False 
        
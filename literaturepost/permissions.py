from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS

class SuperUserByPassPermission(BasePermission):
    perm_map={
        'GET':'view',
        'POST':'add',
        'PUT':'edit',
        'PATCH':'edit',
        'DELETE':'delete',
    }
    action=None
    def get_code_name(self,view):
        model_class=view.queryset.model
        app_label=model_class._meta.app_label
        model_name=model_class._meta.model_name
        return f"{app_label}.can_{self.action}_{model_name}"
    
    def has_permission(self,request,view):
        if request.user.is_superuser:
            return True
        else:
            return self.has_custom_permission(request,view)
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            return self.has_custom_object_permission(request,view,obj)
    
    def has_extra_permission(self,request, view):
        self.action=self.perm_map.get(request.method)
        codename=self.get_code_name(view)
        return request.user.has_perm(codename)
    
    def has_extra_object_permission(self,request,view,obj):
        self.action=self.perm_map.get(request.method)
        codename=self.get_code_name(view)
        return request.user.has_perm(codename) and obj.created_by.role in ['CR','ST']
      
class CanView(BasePermission):
    def has_permission(self, request, view):
        return True
    def has_object_permission(self, request, view, obj):
        return True

class CanAddLiterature(SuperUserByPassPermission):
    def has_custom_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        if request.user.role in ['AD','ST','CR']:
            return True
        else:
            return self.has_extra_permission(request,view)
    def has_custom_object_permission(self,request,view,obj):
        print(f'File: {__file__}:: {request.method}')
        print(obj)
class RoleBasedObjectPermission(SuperUserByPassPermission):
    def has_custom_permission(self, request, view):
            return True
    def has_custom_object_permission(self, request, view, obj):
        user=request.user
        try:
            if request.method in SAFE_METHODS:
                return True
            if user==obj.created_by.user:
                return True
            else:
                actor_role=request.user.userprofile.role
                target_role=obj.created_by.userproifle.role
                if actor_role=='AD':
                    return target_role in ['ST','CR']
                elif actor_role=='ST':
                    return target_role =='CR'
                else:
                    super().has_extra_object_permission(self,request,view,obj)

        except AttributeError:
            return False
        return False


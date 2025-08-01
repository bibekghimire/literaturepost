from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from django.shortcuts import get_object_or_404
from userprofile.models import UserProfile

def is_Self(user, target):
    return user==target

def is_superior(user,target):
    if user.role=='AD':
        return target.role != 'AD'
    elif user.role=='ST':
        return target.role=='CR'
    return False
def isAdmin(user):
    return user.role and user.role=='AD'
def isStaff(user):
    return user.role and user.role=='ST'
def isCreator(user):
    return user.role and user.role=='CR'

def superiorPermission(user, target):
    if not target.role:
        return user.role!='CR'
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if isAdmin(user):
        return isStaff(target) or isCreator(target)
    elif isStaff(user):
        return isCreator(target)

class SuperUserBypassPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        else:
            return self.custom_has_permission(request, view)
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            return self.custom_has_object_permission(request, view, obj)

class CanCreateResetUser(SuperUserBypassPermission):
    '''Only Admins and staffs can create user
    users Other than staff and admin cannot do create user
    '''
    def custom_has_permission(self, request, view):
        role=getattr(request.user,'role')
        if role and role in ['AD','ST']:
            return True
    def custom_has_object_permission(self,request,view,obj):
        user=request.user
        target_user=obj
        return superiorPermission(user,target_user)

class CanUpdateUserName(SuperUserBypassPermission):
    '''Only self, and superior can change username'''
    def custom_has_permission(self, request, view):
        return request.user.is_authenticated
    def custom_has_object_permission(self, request, view, obj):
        user=request.user
        target_user=obj
        if user==target_user:
            return True
        else:
            return superiorPermission(user,target_user)

class CanChangePassword(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return request.user==obj

class CanManageUserProfile(SuperUserBypassPermission):
    """
    - Admins can manage STAFF and CREATORS, but not other ADMINS.
    - Staff can manage only CREATORS.
    - Creators cannot manage anyone.
    """
    def custom_has_object_permission(self, request, view, obj):
        current_role=getattr(request.user,'role',None)
        target_role=getattr(obj,'role',None)
        if not current_role:
            return False
        if request.user==obj.user:
            return True
        if current_role=='AD':
            "Admin can update other than Admin's Profile"
            return target_role != 'AD'
        elif current_role=='ST':
            "Staff can update Creators Profile"
            return target_role == 'CR'
        else:
            return False
    def custom_has_permission(self, request, view):
        role=getattr(request.user,'role',None)
        if not role:
            return False
        return request.user.role in ['AD','ST','CR']
        
class CanCreateUserProfile(SuperUserBypassPermission):
    def custom_has_permission(self, request, view):
        role=getattr(request.user,'role',None)
        if role:
            return role in ['AD','ST']
    def custom_has_object_permission(self,request,view,obj):
        user=request.user
        target=obj.user
        if is_superior(user,target):
            return True

### COntents 

class CanManageContent(SuperUserBypassPermission):
    def custom_has_permission(self,request,view):
        if request.user.is_authenticated:
            return True
        return request.method in SAFE_METHODS
    
    def custom_has_object_permission(self,request,view,obj):
        user=request.user
        target=obj.created_by.user
        if request.method in SAFE_METHODS:
            return True
        if user==target or is_superior(user,target):
            return True


def get_object(view):
    public_id=view.kwargs.get('uuid',None)
    if public_id:
        return get_object_or_404(UserProfile.objects.all(),public_id=public_id)    

class UserPanelPermission(SuperUserBypassPermission):
    def custom_has_permission(self,request,view):
        userprofile=get_object(view)
        user=request.user
        target=userprofile.user
        print(f"{user.role} is requesting {target.role}")
        return is_Self(request.user,userprofile.user) or is_superior(request.user,userprofile.user)
    def custom_has_object_permission(self,request,view,obj):
        user=request.user
        target=obj.created_by.user
        print(f"{user.role} is requesting {target.role}")
        return is_Self(user,target) or is_superior(user,target)
    
class AdminPanelPermission(SuperUserBypassPermission):
    def custom_has_permission(self,request,view):
        user=request.user
        if user.role=='AD':
            return True
    def custom_has_obj_permission(self,request,view,obj):
        user=request.user
        target=obj.created_by
        if isAdmin(user) and not target.is_superuser():
            return True
    

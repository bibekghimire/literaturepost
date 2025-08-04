from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from django.shortcuts import get_object_or_404
from userprofile.models import UserProfile
from utils import choices

ADMIN=choices.RoleChoices.ADMIN
STAFF=choices.RoleChoices.STAFF
CREATOR=choices.RoleChoices.CREATOR

def is_Self(user, target):
    return user==target

def is_superior(user,target):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.role==ADMIN:
        return target.role != ADMIN
    elif user.role==STAFF:
        return target.role==CREATOR
    return False

def isAdmin(user):
    return user.role and user.role==ADMIN

def isStaff(user):
    return user.role and user.role==STAFF

def isCreator(user):
    return user.role and user.role==CREATOR



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
    '''Only Admins and staffs can create a user
    users Other than staff and admin cannot do create_user
    '''
    def custom_has_permission(self, request, view):
        role=getattr(request.user,'role', None)
        if role and role in [ADMIN, STAFF]:
            return True
    def custom_has_object_permission(self,request,view,obj):
        user=request.user
        target_user=obj
        return is_superior(user,target_user)

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
            return is_superior(user,target_user)

class CanChangePassword(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return request.user==obj

#USER PROFILE
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
        if current_role==ADMIN:
            "Admin can update other than Admin's Profile"
            return target_role != ADMIN
        elif current_role==STAFF:
            "Staff can update Creators Profile"
            return target_role == CREATOR
        else:
            return False
    def custom_has_permission(self, request, view):
        role=getattr(request.user,'role',None)
        if not role:
            return False
        return request.user.role in [ADMIN,STAFF,CREATOR]
        
class CanCreateUserProfile(SuperUserBypassPermission):
    'Only Admin and Staff user create a userprofile'
    'and assign a user to it'
    def custom_has_permission(self, request, view):
        role=getattr(request.user,'role',None)
        if role:
            return role in [ADMIN,STAFF]
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
        if user.role==ADMIN:
            return True
    def custom_has_obj_permission(self,request,view,obj):
        user=request.user
        target=obj.created_by
        if isAdmin(user) and not target.is_superuser():
            return True
    

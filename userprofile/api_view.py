# from rest_framework import request
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from . import serializers as _serializers
from .models import UserProfile
from utils import permissions
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.contrib.auth.models import User


'''
view1: for public and listing usersprofiles only,
    return list with few read only fields
also used by authenticated users to list users and view some details at glance. 
'''


#to filter_out the queryset based on requested User
def filter_query_set(self,qs):
    '''
    Helper function: returns filtered queryset to list UserProfiles.
    requested by `admin` all user profiles except admins
    requested by staff all creator list
    None for others
    '''
    condition1=Q(role='ST')
    condition2=Q(role='CR')
    if self.request.user.is_authenticated:
        if self.request.user.is_superuser:
            return qs
        if self.request.user.role=='AD':
            return qs.filter(condition1 | condition2)
    return qs.filter(condition2)

# general/publicfor listing users with some read_only fields and retrieve 
class ProfileCreateView(GenericAPIView, mixins.CreateModelMixin):
    '''
    Users that can crete the UserProfiles are ADMIN and STAFF
    '''
    permission_classes=[IsAuthenticated,permissions.CanCreateUserProfile]
    def get_serializer_class(self):
        self.action='create'
        return _serializers.UserProfileSerializer
    def post(self,request,*args,**kwargs):
        return self.create(request,*args,**kwargs)
        
class ProfileListView(GenericAPIView, mixins.ListModelMixin):
    def get_serializer_class(self):
        self.action='list'
        return _serializers.UserProfileSerializer
    def get_queryset(self):
        '''Users can see the userprofile list in the hierarchy down to them
        ADMIN>STAFF>CREATOR, non authenticated can view Creators profile only
        '''
        qs=UserProfile.objects.all()
        return filter_query_set(self,qs)
    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)

class ProfileDetailView(GenericAPIView, mixins.RetrieveModelMixin):
    '''Users can see the userprofile details in the hierarchy down to them
        ADMIN>STAFF>CREATOR, non authenticated can view Creators profile only
        '''
    lookup_field='public_id'
    lookup_url_kwarg='uuid'
    def get_serializer_class(self):
        '''
        non authenticated users can only see the limited details about a Creator
        but authenticated user can see more details down on the hierarchy'''
        self.action='public-retrieve'
        obj=self.get_object()
        user=self.request.user
        target=obj.user
        if permissions.is_Self(user,target) or permissions.is_superior(user, target):
            self.action='retrieve'
        return _serializers.UserProfileSerializer
    def get_queryset(self):
        qs=UserProfile.objects.all()
        return filter_query_set(self,qs)
    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)

class ProfileUpdateDeleteView(GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    lookup_field='public_id'
    lookup_url_kwarg='uuid'
    permission_classes=[IsAuthenticated,permissions.CanManageUserProfile]
    def get_serializer_class(self):
        self.action='update'
        obj=self.get_object()
        if permissions.is_superior(self.request.user,obj.user):
            self.action='super-update'
        return _serializers.UserProfileSerializer
    def get_queryset(self):
        qs=UserProfile.objects.all()
        return filter_query_set(self,qs)
    def put(self,request,*args,**kwargs):
        return self.update(request,*args,**kwargs)
    def patch(self,request,*args,**kwargs):
        return self.partial_update(request,*args,**kwargs)
    def delete(self,request,*args,**kwargs):
        obj=self.get_object()
        user=request.user
        target=obj.user
        if permissions.is_superior(user,target):
            return self.destroy(request,*args,**kwargs)
        return Response("You cannnot Perform the deletion",status=status.HTTP_403_FORBIDDEN)

#create django.contrib.auth.models.User Object
class UserCreateView(
    GenericAPIView, mixins.CreateModelMixin
):
    serializer_class=_serializers.CreateUserSerializer
    permission_classes=[IsAuthenticated,permissions.CanCreateResetUser]
    
    def post(self,request,*args,**kwargs):
        if self.request.user.role=='CR':
            return Response({'Details:':f"You ({self.request.user.role}) are not allowed to create any user"}, status=status.HTTP_403_FORBIDDEN)
        return self.create(request,*args,**kwargs)
    
class UserListView(
    GenericAPIView, mixins.ListModelMixin
):
    permission_classes=[IsAuthenticated,permissions.CanCreateResetUser]
    serializer_class=_serializers.UserSerializer
    queryset=User.objects.all()

    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)

class UserNameUpdateView(
    GenericAPIView, mixins.UpdateModelMixin, mixins.RetrieveModelMixin
):
    permission_classes=[IsAuthenticated,permissions.CanCreateResetUser]
    serializer_class=_serializers.UserNameUpdateSerializer
    def get_object(self):
        profiles=UserProfile.objects.all()
        user_object=get_object_or_404(profiles, public_id=self.kwargs['uuid'])
        self.check_object_permissions(self.request,user_object)
        return user_object.user
    def put(self, request, *args, **kwargs):
        return self.update(request,*args,**kwargs)
    
    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)

class ResetPasswordView(
    GenericAPIView, mixins.UpdateModelMixin
):
    '''only the superior user can reset the password for others
    in hierarchy ADMIN>STAFF>CREATOR
    '''
    permission_classes=[IsAuthenticated, permissions.CanCreateResetUser]
    serializer_class=_serializers.ResetPasswordSerializer
    def get_object(self):
        '''returns the target user to reset the password for'''
        profiles=UserProfile.objects.all()
        profile_object=get_object_or_404(profiles, public_id=self.kwargs['uuid'])
        user_object=profile_object.user
        self.check_object_permissions(self.request,user_object) #checking permission for the atarget user
        return user_object
    def put(self, request,*args, **kwargs):
        return self.update(request,*args,**kwargs)
    def patch(self,request,*args,**kwargs):
        return self.partial_update(request,*args,**kwargs)
    
class ChangePasswordView(
    GenericAPIView, mixins.UpdateModelMixin
):
    permission_classes=[IsAuthenticated]
    def get_object(self):
        return self.request.user
    serializer_class=_serializers.UpdatePasswordSerializer
    def put(self, request,*args, **kwargs):
        return self.update(request,*args,**kwargs)
    def patch(self,request,*args,**kwargs):
        return self.partial_update(request,*args,**kwargs)
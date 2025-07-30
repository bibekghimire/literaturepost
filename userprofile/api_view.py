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
    permission_classes=[IsAuthenticated,permissions.CanCreateUserProfile]
    def get_serializer_class(self):
        self.action='create'
        return _serializers.UserProfileSerializer
    def post(self,request,*args,**kwargs):
        if request.user.is_superuser:
            return self.create(request,*args,**kwargs)
        if request.user.role in ['AD','ST']:
            return self.create(request,*args,**kwargs)
        return Response({'Details:':"You are not allowed to do this"}, status=status.HTTP_403_FORBIDDEN)

class ProfileListView(GenericAPIView, mixins.ListModelMixin):
    def get_serializer_class(self):
        self.action='list'
        return _serializers.UserProfileSerializer
    def get_queryset(self):
        qs=UserProfile.objects.all()
        return filter_query_set(self,qs)
    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)

class ProfileDetailView(GenericAPIView, mixins.RetrieveModelMixin):
    lookup_field='public_id'
    lookup_url_kwarg='uuid'
    def get_serializer_class(self):
        self.action='public-retrieve'
        obj=self.get_object()
        if permissions.superiorPermission(self.request.user,obj.user):
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
        if permissions.superiorPermission(request.user,obj.user):
            self.action='super-update'
        return _serializers.UserProfileSerializer
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

# #for updating self_profile and view details of self profile 
# class ProfileCreateView(GenericAPIView, mixins.CreateModelMixin):
#     permission_classes=[IsAuthenticated, permissions.CanCreateManageUserProfile]
#     serializer_class=_serializers.UserProfileSerializer

#     def post(self,request,*args,**kwargs):
#         print('POST OPERATION')
#         self.action='create'
#         if request.user.is_superuser:
#             return self.create(request,*args,**kwargs)
#         if request.user.role in ['AD','ST']:
#             return self.create(request,*args,**kwargs)
#         return Response({'Details:':"You are not allowed to do this"}, status=status.HTTP_403_FORBIDDEN)

# class ProfileUpdateDeleteView(
#     GenericAPIView, mixins.RetrieveModelMixin,mixins.UpdateModelMixin, 
#     mixins.CreateModelMixin
# ):
#     '''
#     update only
#     To update self profile and update another profiles on lower hierarchy
#     '''
#     permission_classes=[IsAuthenticated, permissions.CanCreateManageUserProfile]
#     lookup_field='public_id'
#     lookup_url_kwarg='uuid'
#     serializer_class=_serializers.UserProfileSerializer
#     # def get_queryset(self):
#     #     qs=UserProfile.objects.all()
#     #     return filter_query_set(self,qs)

#     def get_object(self):
#         qs=UserProfile.objects.all()
#         uuid=self.kwargs['uuid']
#         # if not 'uuid' in self.kwargs:
#         #     uuid=self.request.user.userprofile.public_id
#         # else:
#         #     uuid=self.kwargs['uuid']
#         obj=get_object_or_404(qs,public_id=uuid)
#         self.check_object_permissions(self.request, obj)
#         return obj
    
#     # def get_serializer_class(self, *args, **kwargs):
#     #     instance=self.get_object()
#     #     kwargs['context'] = self.get_serializer_context()
#     #     if isinstance(instance, UserProfile):
#     #         if instance.user==self.request.user:
#     #             return _serializers.SelfUserProfileSerializer
#     #         return _serializers.SuperUserProfileSerialzier
#     #     return Response({},status=400)
      
    
#     def put(self,request,*args,**kwargs):
#         obj=self.get_object()
#         user=request.user
#         target=obj.user
#         if permissions.is_self(user,target):
#             self.action='update'
#         elif permissions.is_superior(user,target):
#                 self.action='super-update'
#         return self.update(request,*args,**kwargs)
#     def patch(self,request,*args,**kwargs):
#         obj=self.get_object()
#         user=request.user
#         target=obj.user
#         if permissions.is_self(user,target):
#             self.action='update'
#         elif permissions.is_superior(user,target):
#                 self.action='super-update'
#         return self.partial_update(request,*args,**kwargs)
#     def delete(self,request,*args,**kwargs):
#         return self.destroy(request,*args,**kwargs)
# # #to create a USerProfile
# # class ProfileCreateView(
# #     GenericAPIView, mixins.CreateModelMixin, mixins.ListModelMixin
# # ):
# #     serializer_class=_serializers.SuperUserProfileSerialzier
# #     permission_classes=[IsAuthenticated,]
# #     def post(self,request,*args,**kwargs):
# #         if request.user.is_superuser:
# #             return self.create(request,*args,**kwargs)
# #         if request.user.role =='CR':
# #             return Response({'Details:':"You are not allowed to do this"}, status=status.HTTP_403_FORBIDDEN)
# #         return self.create(request,*args,**kwargs)
 
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
    permission_classes=[IsAuthenticated, permissions.CanCreateResetUser]
    serializer_class=_serializers.ResetPasswordSerializer
    # lookup_url_kwarg='uuid'
    # lookup_field='public_id'
    # queryset=UserProfile.objects.all()
    def get_object(self):
        profiles=UserProfile.objects.all()
        profile_object=get_object_or_404(profiles, public_id=self.kwargs['uuid'])
        user_object=profile_object.user
        self.check_object_permissions(self.request,user_object)
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
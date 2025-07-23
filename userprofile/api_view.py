# from rest_framework import request
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from . import serializers
from .models import UserProfile
from . import permissions
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status


'''
view1: for public and listing usersprofiles only,
    return list with few read only fields
also used by authenticated users to list users and view some details at glance. 
'''

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

class PublicProfileView(GenericAPIView,
                        mixins.ListModelMixin, 
                        mixins.RetrieveModelMixin):
    '''
        for listing users with some read_only fields and retrieve a user with some fields
        the public fields and does not requires authentication.
        for public and staff, only creators are returned 
        and for Admin, staffs and creators are returned
        but admin. 
    '''
    serializer_class=serializers.PublicProfileSerializer
    def get_queryset(self):
        qs=UserProfile.objects.all()
        return filter_query_set(self,qs)
    lookup_field='public_id'
    lookup_url_kwarg='uuid'
    def get(self,request,*args,**kwargs):
        if 'uuid' in kwargs:
            return self.retrieve(request,*args,**kwargs)
        return self.list(request,*args, **kwargs)
    
class ProfileDetailUpdateView(
    GenericAPIView, mixins.RetrieveModelMixin,mixins.UpdateModelMixin
):
    '''
    update only
    To update self profile and update another profiles on lower hierarchy
    '''
    permission_classes=[IsAuthenticated, permissions.CanCreateManageUserProfile]
    lookup_field='public_id'
    lookup_url_kwarg='uuid'
    def get_queryset(self):
        qs=UserProfile.objects.all()
        return filter_query_set(self,qs)

    def get_object(self):
        qs=UserProfile.objects.all()
        if not 'uuid' in self.kwargs:
            uuid=self.request.user.userprofile.public_id
        else:
            uuid=self.kwargs['uuid']
        obj=get_object_or_404(qs,public_id=uuid)
        self.check_object_permissions(self.request, obj)
        return obj
    def get_serializer(self, *args, **kwargs):
        instance=self.get_object()
        kwargs['context'] = self.get_serializer_context()
        if isinstance(instance, UserProfile):
            if instance.user==self.request.user:
                return serializers.UserProfileDetailUpdateSerializer(*args,**kwargs)
            return serializers.SuperUpdateProfileSerializer(*args,**kwargs)
        return Response({},status=400)
    def get(self, request,*args,**kwargs):
        print("fetching object")
        return self.retrieve(request,*args,**kwargs)
    
    def put(self,request,*args,**kwargs):
        return self.update(request,*args,**kwargs)
    def patch(self,request,*args,**kwargs):
        print("in PAT")
        return self.partial_update(request,*args,**kwargs)


class ProfileCreateView(
    GenericAPIView, mixins.CreateModelMixin
):
    serializer_class=serializers.CreateProfileSerializer
    permission_classes=[IsAuthenticated,]
    
    def post(self,request,*args,**kwargs):
        if request.user.is_superuser:
            return self.create(request,*args,**kwargs)
        if request.user.role =='CR':
            return Response({'Details:':"You are not allowed to do this"}, status=status.HTTP_403_FORBIDDEN)
        return self.create(request,*args,**kwargs)
    
class UserCreateView(
    GenericAPIView, mixins.CreateModelMixin
):
    serializer_class=serializers.CreateUserSerializer
    permission_classes=[IsAuthenticated,permissions.CanCreateManageUserProfile]
    
    def post(self,request,*args,**kwargs):
        if self.request.user.role=='CR':
            return Response({'Details:':"You are not allowed to create any user"}, status=status.HTTP_403_FORBIDDEN)
        return self.create(request,*args,**kwargs)
    


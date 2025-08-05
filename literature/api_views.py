from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from . import serializers
from .models import Chhanda, Poem, Gajal, Story
from rest_framework.permissions import IsAuthenticated
from .choices import Status
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import BadRequest
# from utils import permissions as permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from utils import permissions
from userprofile.models import UserProfile

from .paginators import CustomPaginator
serializer_model_map={
    'serializer':{
        'poem':serializers.PoemSerializer,
        'story':serializers.StorySerializer,
        'gajal':serializers.GajalSerializer,
        'chhanda':serializers.ChhandaSerializer
    },
    'model':{
        'poem':Poem,
        'story':Story,
        'gajal':Gajal,
        'chhanda':Chhanda,
    }
}
 
class LiteratureListCreateViews(
    GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin
):
    _name='public'
    permission_classes=[permissions.CanManageContent]
    lookup_field='id'
    pagination_class=CustomPaginator
    # lookup_url_kwarg='id'
    # paginator=PageNumberPagination()
    def get_serializer_class(self):
        #handle Key Error
        self.action = 'create' if self.request.method == 'POST' else 'list'
        serializer=serializer_model_map['serializer'][self.kwargs['type']]
        print(serializer)
        return serializer
    # def filter_queryset(self, queryset):
    #     return super().filter_queryset(queryset)
    def get_queryset(self):
        #handle Key Error
        try:
            qs= serializer_model_map['model'][self.kwargs['type']].objects.all()
            return qs.filter(Q(publish_status='PB')) 
        except KeyError:
            raise BadRequest()
    
    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)
    
    def post(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return Response("You are not allowed to create Contents",status=status.HTTP_403_FORBIDDEN)
        return self.create(request,*args,**kwargs)

class LiteratureRetrieveUpdateDeleteView(
    GenericAPIView, mixins.RetrieveModelMixin,mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    _name='public'
    lookup_field='id'
    permission_classes=[permissions.CanManageContent]
    def get_serializer_class(self):
        self.action = 'update' if self.request.method in['PUT','PATCH'] else 'retrieve'
        return serializer_model_map['serializer'][self.kwargs['type']]
    def get_queryset(self):
        try:
            return serializer_model_map['model'][self.kwargs['type']].objects.all().filter(Q(publish_status='PB'))
        except KeyError:
            raise BadRequest()
    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)
    def put(self,request,*args,**kwargs):
        return self.update(request,*args,**kwargs)
    def patch(self,request,*args,**kwargs):
        return self.partial_update(request,*args,**kwargs)
    def delete(self,request,*args,**kwargs):
        return self.destroy(request,*args,**kwargs)

## User_Panel Views    
class UserLiteratureListView(GenericAPIView,mixins.ListModelMixin):
    '''#Any user who is in higher position in rank can view all the contents
    of the user in lower rank, whether it is published, draft or archieved. 
    requires target_user's public_id
    '''
    _name='user'
    pagination_class=CustomPaginator
    permission_classes=[IsAuthenticated,permissions.UserPanelPermission]
    lookup_url_kwarg='id'
    lookup_field='id'
    def get_serializer_class(self):
        #handle Key Error
        self.action = 'list'
        serializer=serializer_model_map['serializer'][self.kwargs['type']]
        return serializer
    def get_queryset(self):
        #handle Key Error
        try:
            userprofile=get_object_or_404(UserProfile.objects.all(),public_id=self.kwargs['uuid'])
            model=serializer_model_map['model'][self.kwargs['type']]
            qs= model.objects.filter(created_by=userprofile)
            return qs
        except KeyError:
            raise BadRequest()
    def get(self,request,*args, **kwargs):
        print(request.user.username)
        if not 'uuid' in kwargs:
            kwargs['uuid']=request.user.userprofile.public_id
        # userprofile=UserProfile.objects.get(public_id=self.kwargs['uuid'])
        # user=request.user
        # if permissions.is_superior(user,userprofile.user) or permissions.is_Self(user,userprofile.user):
        return self.list(request,*args,**kwargs)
        # return Response(f"{request.user}: You Do Not Have Permission To View")

class UserLiteratureRetrieveUpdateDeleteView(
    GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
)  :
    _name='user'
    permission_classes=[IsAuthenticated, permissions.UserPanelPermission]
    lookup_url_kwarg='id'
    lookup_field='id'
    def get_serializer_class(self):
        self.action = 'update' if self.request.method in['PUT','PATCH'] else 'retrieve'
        return serializer_model_map['serializer'][self.kwargs['type']]
    def get_queryset(self):
        try:
            userprofile=get_object_or_404(UserProfile.objects.all(),public_id=self.kwargs['uuid'])
            model=serializer_model_map['model'][self.kwargs['type']]
            qs=model.objects.all()
            return qs
        except KeyError:
            raise BadRequest
    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)
    def put(self,request,*args,**kwargs):
        return self.update(request,*args, **kwargs)
    def patch(self,request,*args,**kwargs):
        return self.partial_update(request,*args,**kwargs)
    def delete(self,request,*args,**kwargs):
        return self.delete(request,*args,**kwargs)

class AdminLiteratureListView(GenericAPIView, mixins.ListModelMixin):
    _name='admin'
    permission_classes=[IsAuthenticated,permissions.AdminPanelPermission]
    def get_serializer_class(self):
        #handle Key Error
        self.action = 'list'
        serializer=serializer_model_map['serializer'][self.kwargs['type']]
        return serializer
    def get_queryset(self):
        #handle Key Error
        try:
            model=serializer_model_map['model'][self.kwargs['type']]
            qs= model.objects.all()
            return qs
        except KeyError:
            return Response("Bad Request",status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)

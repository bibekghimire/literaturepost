from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from . import serializers
from .models import Chhanda, Poem, Gajal, Story
from rest_framework.permissions import IsAuthenticated
from .choices import Status
from rest_framework.response import Response
from rest_framework import status
from literaturepost import permissions as permissions_
from rest_framework.pagination import PageNumberPagination

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
    permission_classes=[permissions_.CanAddLiterature]
    lookup_field='id'
    pagination_class=CustomPaginator
    # lookup_url_kwarg='id'
    # paginator=PageNumberPagination()
    def get_serializer_class(self):
        #handle Key Error
        self.action = 'create' if self.request.method == 'POST' else 'list'
        serializer=serializer_model_map['serializer'][self.kwargs['type']]
        return serializer
    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)
    def get_queryset(self):
        #handle Key Error
        try:
            return serializer_model_map['model'][self.kwargs['type']].objects.all()
        except KeyError:
            return Response("Bad Request",status=status.HTTP_400_BAD_REQUEST)
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
    lookup_field='id'
    permission_classes=[permissions_.RoleBasedObjectPermission]
    def get_serializer_class(self):
        self.action = 'update' if self.request.method in['PUT','PATCH'] else 'retrieve'
        return serializer_model_map['serializer'][self.kwargs['type']]
    def get_queryset(self):
        return serializer_model_map['model'][self.kwargs['type']].objects.all()
    def get(self,request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)
    def put(self,request,*args,**kwargs):
        return self.update(request,*args,**kwargs)
    def patch(self,request,*args,**kwargs):
        return self.partial_update(request,*args,**kwargs)
    def delete(self,request,*args,**kwargs):
        return self.destroy(request,*args,**kwargs)
    
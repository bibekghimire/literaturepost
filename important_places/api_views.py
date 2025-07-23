from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin,
    DestroyModelMixin
)
from . import serializers as _serializers
from . import models
from . import paginators

class ImportantPlacesListCreateView(
    GenericAPIView, ListModelMixin, CreateModelMixin
):
    queryset=models.Temple.objects.all()
    pagination_class=paginators.CustomPaginator
    def get_serializer_class(self):
        self.action='create' if self.request.method=='POST' else 'list'
        return _serializers.TempleSerializer
    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)
    def post(self,request,*args,**kwargs):
        return self.create(request,*args,**kwargs)
    
class ImprotantPlacesRetrieveUpdateDeleteView(
    GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
):
    queryset=models.Temple.objects.all()
    lookup_field='id'
    def get_serializer_class(self,request,*args,**kwargs):
        self.action='update' if request.method in ['PUT','PATCH'] else 'retrieve'
        return _serializers.TempleSerializer
    
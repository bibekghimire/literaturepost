from rest_framework import serializers
from .models import Chhanda, Poem, Gajal, Story
from . import choices
from django.contrib.auth.models import User, Permission
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer
from rest_framework.reverse import reverse


class BaseSerializer(serializers.ModelSerializer):
    '''
    Base serializer for Poem, Stroy and Gajal,
    class level fields 
    list_fields=[], Add the fields that you want to have on list purpose
    detail_fields=[] Add the fields that you want to have on detail fields
    update_fields=[] Add the fields that you want to have on updatable fields
    create_fields=[] Add the fields that you want to have on create field
    will be keepulated later by each class that inherits it. 
    A url field(SerializerMethodField) to get the url of the object. 
    returns the url as /<type:model_name>/<id:object.id>
    keep_fields(self,fields) keeps all the fields form self.fields 
    except those specified in fields parameter. 
    Dynamically instantiates the serializer according to view action
    Automatically pupulates validated_data['created_by'] to request.user
    get_url method is implemented to return the url to specific object
    '''
    list_fields=[]
    detail_fields=[]
    update_fields=[]
    create_fields=[]
    serializer_fields=[]
    url=serializers.SerializerMethodField()
    created_by=UserProfileSerializer(action='list')
    def keep_fields(self, fields):
        '''keeps all the fields except listed in fields'''
        for field in list(self.fields):
                if field not in fields:
                    self.fields.pop(field)

    def __init__(self,*args,**kwargs):
        action_=kwargs.pop('action',None)
        super().__init__(*args,**kwargs)
        action=action_
        if not action_:
            action = self.context.get('view').action if self.context.get('view') else None
        if action == 'list':
            self.keep_fields(self.list_fields)
        elif action == 'retrieve':
            self.keep_fields(self.detail_fields)
        elif action == 'create':
            self.keep_fields(self.create_fields)
        elif action == 'update' or action == 'partial_update':
            self.keep_fields(self.update_fields)
        elif action=='serialize':
            self.keep_fields(self.serialize_fields)
        
    def create(self,validated_data):
        validated_data['created_by']=self.context['request'].user.userprofile
        instance=self.Meta.model(**validated_data)
        instance._validated=True
        instance.save()
        return instance

    def update(self,instance,validated_data):
        instance._validated=True
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        return instance
    
    def get_url(self,obj):
        request=self.context.get('request', None)
        view=self.context.get('view', None)
        if request:
            kwargs={
                    'id':obj.id,
                    'type':obj._meta.model_name,
                }
            if 'uuid' in view.kwargs:
                kwargs['uuid']=view.kwargs['uuid']
            return reverse(
                f'literature:{view._name}-literature-details',
                kwargs=kwargs,
                request=request,
            )

class ChhandaSerializer(BaseSerializer):
    list_fields=['title','url','id']
    create_fields=['title','character_count','details','publish_status']
    detail_fields=['title','character_count','details','created_at','last_modified','created_by','publish_status']
    update_fields=create_fields
    serialize_fields=['title','url']
    class Meta:
        model=Chhanda
        fields='__all__'

class PoemSerializer(BaseSerializer):
    '''
    Model Serializer extending the BaseSerializer
    Model: Poem
    list_fields: 'id','title','created_by','chhanda','url'
    create_fields ('title','chhanda','content','contributors','publish_status')
    update and detail fields are all except id. with read_only fields
    created_by, last_modified, created_at, 
    '''
    chhanda_info=ChhandaSerializer(source='chhanda',read_only=True,action='serialize')
    list_fields=['id','title','created_by','chhanda_info','url','publish_status']
    create_fields=['title','chhanda','content','contributors','publish_status',]
    detail_fields=['id','title','created_by','chhanda_info','content','contributors','created_at','publish_status' ]
    update_fields=create_fields
    class Meta:
        model=Poem
        fields=['created_at', 'contributors', 'content', 'chhanda', 'id', 'created_by', 'title', 'url', 'publish_status','chhanda_info']

    # def to_representation(self, instance):
    #     data=super().to_representation(instance)
    #     data['chhanda_info']=ChhandaSerializer(instance.chhanda,action='serialize')
    #     return data
class StorySerializer(BaseSerializer):
    list_fields=['id','title','created_by','publish_status', 'url']
    create_fields=['title','content','contributors','publish_status',]
    detail_fields=list(set(create_fields+list_fields))+['created_at','last_modified']
    update_fields=create_fields
    
    class Meta:
        model=Story
        fields='__all__'
class GajalSerializer(BaseSerializer):
    list_fields=['id','title','created_by','publish_status', 'url']
    create_fields=['title','content','contributors','publish_status',]
    detail_fields=['id','title','created_by','publish_status','created_at','last_modified', 'content', 'contributors']
    update_fields=create_fields
    
    class Meta:
        model=Gajal
        fields='__all__'  


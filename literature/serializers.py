from rest_framework import serializers
from .models import Chhanda, Poem, Gajal, Story
from . import choices
from django.contrib.auth.models import User, Permission
from userprofile.models import UserProfile
from userprofile.serializers import ListProfileSerializer
from rest_framework.reverse import reverse


class BaseSerializer(serializers.ModelSerializer):
    '''
    Base serializer for Poem, Stroy and Gajal,
    class level fields 
    list_fields=[], Add the fields that you want to have on list purpose
    detail_fields=[] Add the fields that you want to have on detail fields
    update_fields=[] Add the fields that you want to have on updatable fields
    create_fields=[] Add the fields that you want to have on create field
    will be populated later by each class that inherits it. 
    A url field(SerializerMethodField) to get the url of the object. 
    returns the url as /<type:model_name>/<id:object.id>
    pop_fields(self,fields) pops all the fields form self.fields 
    except those specified in fields parameter. 
    Dynamically instantiates the serializer according to view action
    Automatically pupulates validated_data['created_by'] to request.user
    get_url method is implemented to return the url to specific object
    '''
    list_fields=[]
    detail_fields=[]
    update_fields=[]
    create_fields=[]
    url=serializers.SerializerMethodField()
    created_by=ListProfileSerializer()
    def pop_fields(self, fields):
        '''pops all the fields except listed in fields'''
        for field in list(self.fields):
                if field not in fields:
                    self.fields.pop(field)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        action = self.context.get('view').action if self.context.get('view') else None
        if action == 'list':
            self.pop_fields(self.list_fields)
        elif action == 'retrieve':
            self.pop_fields(self.detail_fields)
        elif action == 'create':
            self.pop_fields(self.create_fields)
        elif action == 'update' or action == 'partial_update':
            self.pop_fields(self.update_fields)
        
    def create(self,validated_data):
        validated_data['created_by']=self.context['request'].user.userprofile
        return super().create(validated_data)  
    
    def get_url(self,obj):
        request=self.context.get('request', None)
        if request:
            return reverse(
                'literature:literature-details',
                kwargs={
                    'id':obj.id,
                    'type':obj._meta.model_name,
                },
                request=request,
            )
class ChhandaSerializer(BaseSerializer):
    list_fields=['title','url']
    create_fields=list_fields+['details']
    detail_fields=create_fields+['created_at','last_modified','created_by']
    update_fields=create_fields
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
    list_fields=['id','title','created_by','chhanda','url']
    create_fields=['title','chhanda_choices','content','contributors','publish_status',]
    detail_fields=list(set(create_fields+list_fields))+['created_at','last_modified']
    update_fields=create_fields
    chhanda=serializers.SerializerMethodField(read_only=True)
    # chhanda_choices = serializers.PrimaryKeyRelatedField(
    #     queryset=Chhanda.objects.all(),
    #     source='chhanda',  # this sets the FK in the model
    #     write_only=True,
    # )

    class Meta:
        model=Poem
        fields='__all__'
    def get_fields(self):
        fields=super().get_fields()
        fields['chhanda_choices'] =serializers.IntegerField(
        source='chhanda',  # maps to FK field
        write_only=True,
        required=False  # or False if optional
        )
        return fields

    def get_chhanda(self,obj):
        context=self.context
        return ChhandaSerializer(
            obj.chhanda,
            context=context, 
        ).data

class StorySerializer(BaseSerializer):
    list_fields=['id','title','created_by',]
    create_fields=['title','content','contributors','publish_status',]
    detail_fields=list(set(create_fields+list_fields))+['created_at','last_modified']
    update_fields=create_fields
    
    class Meta:
        model=Poem
        fields='__all__'
class GajalSerializer(BaseSerializer):
    list_fields=['id','title','created_by',]
    create_fields=['title','content','contributors','publish_status',]
    detail_fields=list(set(create_fields+list_fields))+['created_at','last_modified']
    update_fields=create_fields
    
    class Meta:
        model=Poem
        fields='__all__'  


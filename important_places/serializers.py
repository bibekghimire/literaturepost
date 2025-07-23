from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from userprofile.serializers import ListProfileSerializer
from rest_framework.reverse import reverse
from . import models

class BaseSerializer(ModelSerializer):
    list_fields=[]
    detail_fields=[]
    update_fields=[]
    create_fields=[]
    url=serializers.SerializerMethodField()
    created_by= ListProfileSerializer()
    def keep_fields(self,fields):
        '''
        keeps the fields that are specified in the fields argument
        '''
        for field in list(self.fields):
            if field not in fields:
                self.fields.pop(field)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        action=self.context.get('view').action if self.context.get('view') else None
        if action=='list':
            self.keep_fields(self.list_fields)
        if action=='retrieve':
            self.keep_fields(self.detail_fields)
        if action=='create':
            self.keep_fields(self.create_fields)
        if action=='update' or action=='partial_update':
            self.keep_fields(self.update_fields)
        
    def create(self,validated_data):
        validated_data['created_by']=self.context.get('request').user.userprofile
        instance=self.Meta.model(**validated_data)
        instance._validated=True
        instance.save()
        return instance
    def update(self, instance,validated_data):
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance._validated=True
        instance.save()
        return instance
    
    def get_url(self,obj):
        request=self.context.get('request', None)
        if request:
            return reverse(
                'important-place',
                kwargs={
                    'id':object.id,
                    'type':'temple',
                }
            )
        


class TempleSerializer(BaseSerializer):
    list_fields=['title','address','created_by']
    detail_fields=['created_at','last_modified','created_by','title','address','details','image1','image2','image3']
    create_fields=['title','address','details','image1','image2','image3']
    update_fields=create_fields
    class Meta:
        model=models.Temple
        fields='__all__'
        read_only_fields=['id']

    
    


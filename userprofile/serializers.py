from rest_framework import serializers
from .models import UserProfile, UserExtension
from django.contrib.auth.models import User
from . import validators
from utils import choices
from rest_framework.reverse import reverse


#################
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username']
        read_only_fields=['username'] 
## Helper Functions
def check_role_assignment(assigner_role,assigned_role):
    if assigner_role == 'AD':
        return assigned_role in ['ST','CR']
    elif assigner_role=='ST':
        return assigned_role=='CR'
    else:
        return False

class BaseModelSerializer(serializers.ModelSerializer):
    '''
    this serializer provides create and update method
    that sets ._validated as True so that it will be used 
    by save method in models. 
    It s common for all serializers that are to be written in 
    serializers.ModelSerializer
    '''
    url=serializers.SerializerMethodField()
    created_by=UserSerializer()
    list_fields=[]
    create_fields=[]
    detail_fields=[]
    public_detail_fields=[]
    update_fields=[]
    super_update_fields=[]
    user=UserSerializer(read_only=True)
    assign_user=serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.filter(userprofile__isnull=True)
    )

    def keep_fields(self,fields):
        '''
        removes the fields that are not in fields
        from self.fields
        '''
        self_fields=list(self.fields)
        for field in self_fields:
            if field not in fields:
                self.fields.pop(field)
        
    def __init__(self,*args,**kwargs):
        _action=kwargs.pop('action', None)
        super().__init__(*args,**kwargs)
        if self.context.get('view'):
            _action=self.context.get('view').action

        if _action=='list':
            self.keep_fields(self.list_fields)
        elif _action=='create':
            self.keep_fields(self.create_fields)
        elif _action=='retrieve':
            self.keep_fields(self.detail_fields)
        elif _action=='public-retrieve':
            self.keep_fields(self.public_detail_fields)
        elif _action=='update':
            self.keep_fields(self.update_fields)
        elif _action=='super-update':
            self.keep_fields(self.super_update_fields)
        else:
            raise serializers.ValidationError("Must provide an Action")
        
    def validate(self,attrs):
        if 'role' in attrs:
            user=self.context['request'].user
            if user.is_superuser:
                return attrs
            if not check_role_assignment(user.role,attrs['role']):
                raise serializers.ValidationError(f'You are not allowed to assign this Role.{attrs["role"]}')
        return attrs

    def create(self,validated_data):
        validated_data['created_by']=self.context['request'].user
        validated_data['user']=validated_data.pop('assign_user')
        instance=self.Meta.model(**validated_data)
        instance._validated=True
        instance.save()
        return instance
    
    def update(self,instance,validated_data):
        assign_user=getattr(validated_data,'assign_user')
        if assign_user:
            validated_data['user']=assign_user
        validated_data['modified_by']=self.context['request'].user
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance._validated=True
        instance.save()
        return instance

    def get_url(self,obj):
        request=self.context.get('request')
        if request:
            return reverse(
                'userprofile:profile-detail',
                kwargs={
                    'uuid':obj.public_id
                },
                request=request,
            )

class UserProfileSerializer(BaseModelSerializer):
    class Meta:
        model=UserProfile
        fields='__all__'
    list_fields=['display_name','profile_picture','url']
    detail_fields=[
        'first_name','last_name','display_name','email',
        'phone_number','date_of_birth','user','profile_picture','role',
        'status','public_id','created_by'
                ]
    public_detail_fields=['first_name','last_name','display_name','profile_picture','public_id','email']
    update_fields=['first_name','last_name','display_name','email','date_of_birth',
                   'profile_picture',]
    create_fields=[
        'first_name','last_name','display_name','email',
        'phone_number','date_of_birth','assign_user','profile_picture','role',
        'status',
                ]
    super_update_fields=create_fields

##################################################################################
# User related serializers:    
##################################################################################

class CreateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )

    class Meta:
        model=User
        fields=['username','password1','password2']
        extra_kwargs={
            "username": {
                "required": True,
                "read_only": False,
                "label": "Username",
                "help_text": "Required. 3 to 12 characters long, must start with alphabet. Followed by Alpha, digits and _ only",
                "max_length": 12
            },
        }
    def validate_username(self,value):
        value=validators.username_validator(value)
        return value
    
    def validate(self,data):
        if validators.match_password(data['password1'],data['password2']):
            return data
        raise serializers.ValidationError('Both password must match and cannot be empty',code='invalid')

    def create(self,validated_data):
        password=validated_data.pop('password1')
        username=validated_data.pop('username')
        user=User(username=username)
        user.set_password(password)
        user.save()
        created_by=self.context['request'].user
        UserExtension.objects.create(user=user, created_by=created_by)
        return user

class ResetPasswordSerializer(BaseModelSerializer):
    password1 = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
    class Meta:
        model=User
        fields=['username','password1', 'password2']
        read_only_fields=['username']
    def validate(self,data):
        if validators.match_password(data['password1'],data['password2']):
            return data
        raise serializers.ValidationError(detail={
            'message':'Both password must match and cannot be empty',
            'code':'invalid'
        })
    
    def update(self,instance,validated_data):
        assigner=self.context['request'].user
        assigned=instance
        if not assigned.role and assigner.role in ['AD','ST']:
            instance.set_password(validated_data.pop('password1'))
        elif assigned.role:
            if check_role_assignment(assigner.role,assigned.role):
                instance.set_password(validated_data.pop('password1'))
        else:
            raise serializers.ValidationError("You cannot Reset the password for this user")
        instance.save()
        print(instance)
        return instance

class UpdatePasswordSerializer(BaseModelSerializer):
    old_password = serializers.CharField(
    write_only=True, required=True, style={'input_type': 'password'}
    )
    password1 = serializers.CharField(
    write_only=True, required=True, style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
    write_only=True, required=True, style={'input_type': 'password'}
    )
    class Meta:
        model=User
        fields=['username','old_password','password1','password2']
        read_only_fields=['username']
    def validate(self,data):
        if validators.match_password(data['password1'],data['password2']):
            return data
        raise serializers.ValidationError('Both password must match and cannot be empty',code='invalid')
    
    def update(self,instance, validated_data):
        if not self.context['request'].user==instance:
            raise serializers.ValidationError("You cannot change Password for this user")
        if validators.check_password(instance,validated_data['old_password']):
            instance.set_password(validated_data.pop('password1'))
            instance.save()
            print('password updated')
            return instance
        raise serializers.ValidationError("Old Password Incorrect", code='passworderror')

class UserNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','id']
        read_only_fields=['id',]
    def validate_username(self, value):
        validators.username_validator(value)
        return value
  


from rest_framework import serializers
from .models import UserProfile, UserExtension
from django.contrib.auth.models import User
from . import validators
from . import choices
from rest_framework.reverse import reverse



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
    def validate(self,attrs):
        if 'role' in attrs:
            user=self.context['request'].user
            if user.is_superuser:
                return attrs
            if not check_role_assignment(user.role,attrs['role']):
                raise serializers.ValidationError(f'You are not allowed to assign this Role.{attrs["role"]}')
        return attrs

    def create(self,validated_data):
        instance=self.Meta.model(**validated_data)
        instance._validated=True
        instance.save()
        return instance
    
    def update(self,instance,validated_data):
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance._validated=True
        instance.save()
        return instance

class ListProfileSerializer(serializers.ModelSerializer):
    '''for listing userprofiles only with some fields to display'''
    userprofile_url=serializers.SerializerMethodField()
    class Meta:
        model=UserProfile
        fields=['display_name','email','userprofile_url']

    def create(self,validated_data):
        raise serializers.ValidationError("This Serializer is ReadOnly")
    def update(self,validated_data):
        raise serializers.ValidationError("This serializer is ReadOnly")
    
    def get_userprofile_url(self,obj):
            request=self.context.get('request',None)
            if request:
                return reverse('userprofile:userprofile-detail',kwargs={'uuid':obj.public_id}, request=request)

class PublicDetailSerializer(ListProfileSerializer):
    
    class Meta:
        model=ListProfileSerializer.Meta.model
        fields=ListProfileSerializer.Meta.fields+['first_name','last_name','profile_picture',]

    def create(self,validated_data):
        raise serializers.ValidationError("This Serializer is ReadOnly")
    def update(self,validated_data):
        raise serializers.ValidationError("This serializer is ReadOnly")   


class PublicProfileSerializer(BaseModelSerializer):
    '''for listing purpose only
    serializes ['first_name','last_name', 'display_name', 'email','public_id']
    and all are read only for public access.
    '''
    class Meta:
        model=UserProfile
        fields=['first_name','last_name', 'display_name', 'email','public_id','role']
        read_only_fields=fields

class UserProfileDetailUpdateSerializer(BaseModelSerializer):
    '''
    for self detail view and update purpose only 
    'first_name','last_name', 'display_name', 'email','public_id',
            'phone_number','date_of_birth', 'username', 'profile_picture','role',
            'status',
    where read_only fields are: 
    'public_id','phone_number', 'username','role','status'
    They cannot be updated by self account. 
    '''
    username=serializers.CharField(source='user.username')
    class Meta:
        model=UserProfile
        
        fields=[
            'first_name','last_name', 'display_name', 'email','public_id',
            'phone_number','date_of_birth', 'username', 'profile_picture','role',
            'status',
        ]
        read_only_fields=['public_id','phone_number', 'username','role','status']
    
class SuperUpdateProfileSerializer(BaseModelSerializer):
    '''
        for updating User Profiles of lowe level users
        hierarchy who can manage whom:
        Admin>Staff>Creator.
    '''
    username=serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model=UserProfile
        fields=[
            'first_name','last_name', 'display_name', 'email','public_id',
            'phone_number','date_of_birth', 'username', 'profile_picture','role',
            'status',
        ]
        read_only_fields=['public_id', 'username',]
     
class CreateProfileSerializer(BaseModelSerializer):
    '''To create a User Profile, Only Stadd User and Admin User can create 
    '''
    role=serializers.ChoiceField(choices=[])
    status=serializers.ChoiceField(choices=choices.StatusChoices)
    user= serializers.SlugRelatedField(slug_field='username', queryset=User.objects.none())
    #make sure to use another Pkey instead of id like UUID4

    class Meta:
        model=UserProfile
        fields=[
            'first_name','last_name', 'display_name', 'email','public_id',
            'phone_number','date_of_birth', 'user', 'profile_picture',
            'role', 'status',
        ]
        read_only_fields=['public_id']
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        user=self.context['request'].user
        allowed_roles=[]
        if user.is_superuser:
            allowed_roles=[
                (value,label)
                for value,label in choices.RoleChoices.choices]
        elif getattr(user, 'role', None) == 'AD':
            allowed_roles=[
                (value,label)
                for value,label in choices.RoleChoices.choices if value in [choices.RoleChoices.STAFF,choices.RoleChoices.CREATOR]
            ]
        elif  getattr(user, 'role', None) == 'ST':
            allowed_roles=[
                ('CR','CREATOR')
            ]
        self.fields['role'].choices = allowed_roles
        self.fields['user'].queryset=User.objects.filter(userprofile__isnull=True)


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

class ResetpasswordSerializer(BaseModelSerializer):
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
        raise serializers.ValidationError('Both password must match and cannot be empty',code='invalid')
    
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
    def validate(self,data):
        if validators.match_password(data['password1'],data['password2']):
            return data
        raise serializers.ValidationError('Both password must match and cannot be empty',code='invalid')
    
    def update(self,instance, validated_data):
        if not self.context['request.user']==instance:
            raise serializers.ValidationError("You cannot change Password for thsi user")
        if validators.check_password(instance,validated_data['old_password']):
            instance.set_password(validated_data.pop('password1'))
            return instance
        raise serializers.ValidationError("Old Password Incorrect", code='passworderror')
    
from django.db import models
from django.contrib.auth.models import User
import datetime
import os
from PIL import Image
from django.core.exceptions import ValidationError

from . import choices
from utils import validators
import uuid

# Create your models here.
def user_directory_path(instance, filename):
    ext=os.path.splitext(filename)[1] 
    return f'user_{instance.user.id}_{instance.first_name}/profile{ext}'

# def validators.no_whitespace(value):
#     if not value or not value.strip():
#         raise ValidationError('Empy or none value', code='blank')   
#     return value

def get_user_role(self):
    if hasattr(self,'userprofile'):
        return self.userprofile.role
    return None
User.add_to_class('role',property(get_user_role))

class UserExtension(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='extension')
    created_by=models.ForeignKey(User,null=True, on_delete=models.SET_NULL, related_name='created_users')

    def __str__(self):
        return f"Extension of user: {self.user.usernmae}"

class CleanValidatedModel(models.Model):
    """
    Base model that intelligently skips full_clean()
    if the instance was already validated (e.g., via a serializer).
    """
    _validated = False  # Internal flag for validated instances
    created_at=models.DateTimeField("Created At",auto_now_add=True)
    class Meta:
        abstract = True  # Don't create a DB table for this
        permissions=[
            ("can_add_user", "Can add user"),
            ("can_edit_user", "Can edit user"),
            ("can_reset_password", "Can reset password"),
            ("can_delete_user", "Can delete user"),
            ("can_change_user_status", "Can change user status"),
            ("can_assign_admin_role", "Can assign admin role"),
            ("can_assign_staff_role", "Can assign staff role"),
            ("can_assign_creator_role", "Can assign creator role"),
            ("can_add_userprofile", "Can add user profile"),
            ("can_edit_user_profile", "Can edit user profile"),
            ("can_delete_user_profile", "Can delete user profile"),

        ]

    def save(self, *args, **kwargs):
        # Only call full_clean if validation hasn’t run yet
        if not self._validated:
            print("validating invalidated data")
            self.full_clean()
        super().save(*args, **kwargs)

class UserProfile(CleanValidatedModel):
    '''
    This model has following fields:
    1. status: Whether the profile is active, suspended or deleted
        ACT, SUS, DEL
    2. role: Indicates the role of the profile (Admin, staff and Creator)
        AD, ST, CR
    3. display_name(max 65 char): This name will be used as display name in UI. Default=full name
        and must contain only alphabets. 
    4. first_name: First Name (32 char alphabets only)
    5. last_name: Last Name (32 char alphabets only)
    6. email: must be in valid e-mail format and unique for each
    7. phone_number: 10 digit nepali phone number and unique
    8. user: is the one to one field to django.contrib.auth.models.User class
    9. created: autofield and assigned when the object is created
    10. profile_picture: Display picture, valid image file only 400x400.
    '''
    class Meta:
        permissions = CleanValidatedModel._meta.permissions 
    first_name=models.CharField(
        "First Name", max_length=32,
        validators=[validators.no_whitespace,validators.name_validator]
    )
    
    last_name=models.CharField(
        "Last Name", max_length=32,
        validators=[validators.no_whitespace,validators.name_validator],
    )
    
    display_name=models.CharField(
        "Display Name", max_length=65, null=True, blank=True,
        validators=[validators.no_whitespace,validators.name_validator],
    )
    
    email=models.EmailField(unique=True,validators=[validators.no_whitespace,])
    
    phone_number=models.CharField(
        "Phone Number",unique=True, max_length=10,
        validators=[validators.no_whitespace,validators.phone_number_validator],
    )
    
    date_of_birth=models.DateField("Date of Birth",validators=[validators.age_validator])
    
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    
    profile_picture=models.ImageField(
        "Profile Picture", blank=True,
        upload_to=user_directory_path,
        validators=[validators.profile_picture_validator],
    )
    
    role=models.CharField(
        "User Roles",
        null=True,
        max_length=2,
        choices=choices.RoleChoices.choices,
    )
    
    status=models.CharField(
        "Status",
        null=True, max_length=3,
        choices=choices.StatusChoices.choices,
    )
    
    public_id=models.UUIDField("Public ID", default=uuid.uuid4, editable=False,unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.role}, {self.id}: {self.user.username}'
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self, *args, **kwargs):
        try:
            old=UserProfile.objects.get(pk=self.pk)
            if old.profile_picture and old.profile_picture != self.profile_picture:
                if os.path.isfile(old.profile_picture.path):
                    os.remove(old.profile_picture.path)
        except UserProfile.DoesNotExist:
            pass
        if not self.display_name.strip():
            self.display_name=self.get_full_name()
        super().save(*args,**kwargs)

    # def clean(self):
        # '''
        # Checks for validations of the fields:
        # collects each field errors as a dictionary
        # key: field name
        # value: list of collected errors
        # '''
        # errors={}
        # super().clean()
        # field_validators=[
        #     ('date_of_birth',self.date_of_birth,[validators.age_validator]),
        #     ('display_name',self.display_name,[validators.name_validator,]),
        #     ('first_name',self.first_name,[validators.name_validator,]),
        #     ('last_name',self.last_name, [validators.name_validator]),
        #     ('phone_number',self.phone_number,[validators.phone_number_validator,unique_validator]),
        #     ('email',self.email,[unique_validator]),
        #     ('profile_picture',self.profile_picture,[validators.image_validator]),
        # ]
        # for field_name, value, validator_list in field_validators:
        #     field_errors=[]
        #     for validator_func in validator_list:
        #         validator_func(self,field_name,value=value,errors=field_errors)
        #     if field_errors:
        #         errors[field_name]=field_errors
        # if errors:
        #     # print(errors)
        #     raise ValidationError(errors)



    
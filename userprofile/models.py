from django.db import models
from django.contrib.auth.models import User
import datetime
import os
from PIL import Image
from django.core.exceptions import ValidationError

from ..utils import choices
from utils import validators
import uuid

# Create your models here.
def user_directory_path(instance, filename):
    ext=os.path.splitext(filename)[1] 
    return f'user_{instance.user.id}_{instance.first_name}/profile{ext}'

'''
The role is defined here in UserProfile, accessing role associated to UserProfile
that has foriegn key to Django.contrib.auth.models.User is a bit lengthy
user.profile.role, so we defined a method that returns
user.userprofile.role
'''
def get_user_role(self):
    if hasattr(self,'userprofile'):
        return self.userprofile.role
    return None
User.add_to_class('role',property(get_user_role))

class UserExtension(models.Model):
    '''
    This UserExtension model with two fields:
    1. user: OneToOneField to django.contrib.auth.models.User the user created
    2. created_by: ForeignKey to django.contrib.auth.models user who created 
    the user 'user'
    '''
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
    created_by=models.ForeignKey(User,related_name='created_profiles',on_delete=models.PROTECT, editable=False, null=True)
    last_modified=models.DateTimeField("Last Modified",auto_now=True)
    modified_by=models.ForeignKey(User,related_name='modified_profiles',on_delete=models.PROTECT,null=True)
    class Meta:
        abstract = True  # Don't create a DB table for this

    def save(self, *args, **kwargs):
        # Only call full_clean if validation hasn’t run yet
        if not self._validated:
            self.full_clean()
            self._validated=False
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
        null=True,
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
    
    public_id=models.UUIDField("Public ID", default=uuid.uuid4, editable=False,unique=True,)
    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.role}, {self.id}: {self.user.username}'
    @property
    def full_name(self):
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
            self.display_name=self.full_name
        super().save(*args,**kwargs)

    
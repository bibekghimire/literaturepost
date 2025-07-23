from django.db import models
from userprofile.models import UserProfile
import os
from functools import partial
from utils import validators
# Create your models here.

def get_file_upload(instance,filename,file):
    ext=os.path.splitext(filename)[1]
    return f'temple/{instance.id}/{file}{ext}'

class CleanValidatedModel(models.Model):
    """
    Base model that intelligently skips full_clean()
    if the instance was already validated (e.g., via a serializer).
    or calls the full_clean if not. 
    """
    class Meta:
        abstract=True
        ordering=['last_modified','created_at']

    
    _validated=False
    created_at=models.DateTimeField("Created", auto_now_add=True)
    last_modified=models.DateTimeField("Last Modified", auto_now=True)
    created_by=models.ForeignKey(
        UserProfile, related_name="%(class)s_added", on_delete=models.PROTECT, editable=False
    )
    
    def save(self,*args,**kwargs):
        if not self._validated:
            self.full_clean()
        super().save(*args,**kwargs)
    @property
    def author(self):
        return self.created_by.display_name
    
class Temple(CleanValidatedModel):
    title=models.CharField("Temple",max_length=100)
    address=models.CharField("Address", max_length=100)
    # location=models.PointField("GPS Location", required=False)#future Use
    details=models.TextField("Details")
    image1=models.ImageField("Image 1",validators=[validators.image_validator],upload_to=partial(get_file_upload,file='image1'), blank=True, null=True)
    image2=models.ImageField("Image 2",validators=[validators.image_validator],upload_to=partial(get_file_upload,file='image2'),blank=True, null=True)
    image3=models.ImageField("Image 3",validators=[validators.image_validator],upload_to=partial(get_file_upload,file='image3'),blank=True, null=True)


    def save(self,*args,**kwargs):
        try:
            old=Temple.objects.get(pk=self.pk)
            for field in ['image1','image2','image3']:
                old_image=getattr(old,field)
                new_image=getattr(self,field)
                if old_image and old_image != new_image:
                    if os.path.isfile(old_image.path):
                        os.remove(old_image.path) 
        except Temple.DoesNotExist:
            pass
        super().save(*args, **kwargs)


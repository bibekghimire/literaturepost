from django.db import models
from userprofile.models import UserProfile
from .choices import Status
from utils import validators
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class CleanValidatedModel(models.Model):
    """
    Base model that intelligently skips full_clean()
    if the instance was already validated (e.g., via a serializer).
    """
    _validated = False  # Internal flag for validated instances
    created_at=models.DateTimeField("Created At",auto_now_add=True,)
    last_modified=models.DateField("Modified At", auto_now=True)
    created_by=models.ForeignKey(UserProfile, related_name="%(class)s_added", on_delete=models.PROTECT,editable=False)
    class Meta:
        abstract = True  # Don't create a DB table for this
        ordering=['last_modified','created_at']

    def save(self, *args, **kwargs):
        # Only call full_clean if validation hasn’t run yet
        if not self._validated:
            self.full_clean()
        super().save(*args, **kwargs)
    @property
    def author(self):
        return self.created_by.display_name

class Literature(CleanValidatedModel):
    ''' 
    base class for all other Literatures
    has title, author(FK with UserProfile) contributors
    '''
    class Meta:
        abstract=True
    title=models.CharField(max_length=100, validators=[validators.no_whitespace])
    contributors=models.CharField("Contributors",max_length=200,)
    content=models.TextField()
    publish_status=models.CharField(max_length=2,verbose_name="publish Status",choices=Status.choices, default=Status.DRAFT)

class Chhanda(CleanValidatedModel):
    title=models.CharField(max_length=50,validators=[validators.name_validator], unique=True)
    character_count=models.SmallIntegerField(
        verbose_name='total characters',
        validators=[MinValueValidator(5,message="If it contains value less than 5 please contact Admin")]
    )
    details=models.TextField() #redundant to content
    class Meta:
        ordering=['title']
        permissions=[
            ('can_edit_chhanda','Can Edit Chhanda'),
            ('can_delete_chhanda','Can Delete Chhanda'),
            ('can_add_chhanda','Can Add Chhanda')
        ]
    
    def __str__(self):
        return self.title +' : ' + str(self.character_count)


class Poem(Literature):

    '''
    The Poem Class extends Literature 
    extra field chhanda, foreign key to Chhanda Model
    '''
    chhanda=models.ForeignKey('Chhanda',related_name='poems', null=True, on_delete=models.SET_NULL, blank=True)
    def __str__(self):
        return f'{self.title}: {self.author}'
    class Meta:
        ordering=['last_modified']
        permissions=[
            ('can_edit_poem', 'Can Edit Poem'),
            ('can_delete_poem', 'Can Delete Poem'),
            ('can_add_poem', 'Can Add Poem'),
            ('can_archieve_poem','Can Archieve Poem'),
        ]
    
class Gajal(Literature):
    def __str__(self):
        return f'{self.title}: {self.author}'
    
    class Meta:
        ordering=['last_modified']
        permissions=[
           ('can_edit_gajal', 'Can Edit Gajal'),
           ('can_delete_gajal', 'Can Delete Gajal'),
           ('can_add_gajal', 'Can Add Gajal'),
           ('can_archieve_gajal','Can Archieve Gajal'), 
        ]

class Story(Literature):
    def __str__(self):
        return f'{self.title}: {self.author}'
    class Meta:
        ordering=['last_modified']
        permissions=[
            ('can_edit_story', 'Can Edit Story'),
            ('can_delete_story', 'Can Delete Story'),
            ('can_add_story', 'Can Add Story'),
            ('can_archieve_story','Can Archieve Story'),
        ]


    

from django.db import models

# class LiteratureTypes(models.TextChoices):
#     GAJAL='GL', 'Gajal'
#     MUKTAK='MK', 'Muktak'
#     KABITA='KB', 'Kabita'
#     HIEKU='HK', 'Hieku'

class Status(models.TextChoices):
    ARCHIVED='AR', 'Archieved'
    DRAFT='DR', "Draft"
    PUBLISHED='PB', "Published"
from django.core.exceptions import ValidationError
import re
import regex as ure
import os
import io
from PIL import Image
from datetime import date
import unicodedata

from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile

def no_whitespace(value):
    value = unicodedata.normalize('NFC', value)
    if not value or not value.strip():
        raise ValidationError('Empy or none value', code='blank')   
    return value

def crop_compress(img,size=(300,300), max_size=2):
    '''
        Receives Image and returns Image cropped to size 
        compressed to max_size(MB) default 2MB
    '''
    target_width,target_height=size
    width,height=img.size
    left=(width-target_width)//2 if width>target_width else 0
    top=(height-target_height)//2 if height>target_height else 0
    right=left+min(width,target_width)
    bottom=top+min(height,target_height)
    img=img.crop((left,top,right,bottom))
    buffer=io.BytesIO()
    quality=85
    img.save(buffer,format='JPEG', quality=quality)
    while buffer.tell()>max_size*1024*1024 and quality>20:
        quality-=5
        img.save(buffer,format='JPEG', quality=quality)
    buffer.seek(0)
    return ContentFile(buffer.getvalue(), name="profile.jpg")

def phone_number_validator(value,errors=...): 
    '''The phone number must match the pattern '^[9][87]{1}[0-9]{8}$'
     The valid mobile number must start with 98 or 97 followed by 8 digit 
     Errors: code-Invalid, "Mobile Number Invalid, 98xxxxxxxx or 97xxxxxxxx"
     Raise ValidationError if errors is Elipsis, if errors is list errors are appended. 
     '''
    pattern=r'^[9][87]{1}[0-9]{8}$'
    local_errors=[]
    if re.match(pattern,value):
        return value
    else:
        local_errors.append(ValidationError("Mobile Number Invalid, 98xxxxxxxx or 97xxxxxxxx",code='invalid'))
    raise ValidationError(local_errors)

def name_validator(value, errors=...):
    'Checks whether the value contains only Unicode literals not other characters'
    'Appends ValidationError with code:"Alphabet" to the list errors if provided'
    'else simply raises ValidationError with code Alphabet'
    'errors:'
    'blank: Tabs and spaces only are not allowed'
    local_errors=[]
    value=no_whitespace(value)
    if not ure.fullmatch(r'[\p{L} ]+', value):
        local_errors.append(ValidationError("Only letters and spaces are allowed (from any language).", code='invalid'))
    if local_errors:
        if isinstance(errors,list):
            errors.append(local_errors)
        else:
            raise ValidationError(local_errors)
    else:
        return value

def username_validator(value, errors=...):
    '''
        'Checks for multiple validation and collects all the errors as list',
        'Raises ValidationError with all collected errors'
        error codes:
        'Pattern': 'Raises if the username didnot match the pattern:
        '^[a-z][a-z0-9_]{2,11}'
        'ReservedWord': 'if 'admin' is included in username
    '''
    local_errors=[]
    value=no_whitespace(value)
    # name_validator(value,errors)
    pattern=r'^[a-z][a-z0-9_]{2,11}$'
    if not re.match(pattern,value):
        local_errors.append(ValidationError(
            "Username starts with only lowercase, followed by lowercase, digits (0-9) or underscore and 3 character to 12 character long",
            code='pattern'
        ))

    if 'admin' in value.lower():
        local_errors.append(ValidationError("Avoid using 'admin' in username",
                                      code='ReservedWord'))
    if local_errors:
        if isinstance(errors,list):
            errors.append(local_errors)
        else:
            raise ValidationError(local_errors)
    return value

def age_validator(value,errors=...):
    '''
    Value must be valid Python datetime.date object. otherwise raises ValidationError code: InvalidFormat
    errors should be a list.
    if errors is list any error occured during validation is appended to it. 
    returns value if the age>=18,
    raise ValidationError if errors is not an instance of list class
    '''
    if not isinstance(value,date):
        error = ValidationError('Invalid date format', code='InvalidFormat')
    else:
        today=date.today()
        age=today.year-value.year - ((today.month,today.day)<(value.month,value.day))
        if age>=18:
            return value
        error=ValidationError('Age must be greater or equal to 18', code='UnderAge')
    if isinstance(errors,list):
            errors.append(error)
            return None
    else:
        raise error

def email_validator(value, errors=...):
    pass

def image_validator(value, errors=...):
        
        if not value:
            return 
        local_errors=[]
        if value.size>=5*1024*1024:
            local_errors.append[ValidationError("File size Too Large",code='LargeFile')]
        else:
            valid_extensions=['.jpg','.jpeg','.png']
            ext=os.path.splitext(value.name)[1].lower()
            if ext not in valid_extensions:
                local_errors.append(ValidationError("Invalid File Extension",code="invalid"))
            else:
                img=Image.open(value)
                try:
                    img.verify()
                except Image.DecompressionBombError:
                    local_errors.append(ValidationError("The file looks Suspecious", code="suspicious")) 

                except Image.UnidentifiedImageError:
                    local_errors.append(ValidationError(
                        "The image is not valid or may be corrupted",
                        code='invalid'
                    ))   
                except Exception as e:
                    local_errors.append(ValidationError('Unknown error occured check the image file', code='unknown'))
        if local_errors:
            if isinstance(errors,list):
                errors.append(local_errors)
            raise ValidationError(local_errors)
        return crop_compress(Image.open(value),size=(400,400),max_size=3)

def check_password(user, password):
    return user.check_password(password)
def match_password(password1, password2):
    if not password1.strip():
        return False
    if not password2.strip():
        return False
    return password1==password2
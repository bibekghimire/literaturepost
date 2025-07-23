from django.test import TestCase
from userprofile.models import UserProfile
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile


from django.contrib.auth.models import User
import datetime

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

error_codes=[
    'max_length','invalid','blank','pattern',
    'ReservedWord','invalid_choice','UnderAge',
    'LargeFile', 'suspicious', 'invalid', 'unknown',
    'InvalidFormat'
]
def get_dummy_image(name="test.jpg", size=(100, 100), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(
        name, buffer.read(),content_type="image/JPEG"
    )

error_codes_messages={
    'first_name':{
        'blank':'Tabs and spaces only are not allowed',
        'invalid':'Only letters and spaces are allowed (from any language)'
    },
    'last_name':{
        'blank':'Tabs and spaces only are not allowed',
        'invalid':'Only letters and spaces are allowed (from any language)'
    },
    'display_name':{
        'blank':'Tabs and spaces only are not allowed',
        'invalid':'Only letters and spaces are allowed (from any language)',
        
    }
}

def get_valid_profile_data():
    return {
    "first_name": u"बिबेक",
    "last_name": "Ghimire",
    "display_name": "BIBEK",
    "email": "bibek@example.com",
    "phone_number": "9840172372",
    "date_of_birth": datetime.date(2000, 5, 3),
    "role": "AD",
    "status": "ACT",
    }
def get_invalid_data():
    return {
    "first_name": ["  ","23","","&","$","_","kjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfnkjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfnkjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfn" ],
    "last_name": ["  ","23","","&","$","_","kjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfnkjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfnkjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfn" ],
    "display_name": ["23","&","$","_","kjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfnkjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfnkjhuurisudhdkfjcnhdyhtieksjdhtywidfalkjfajkfn" ], 
    "email": ["example.com","hhh","___"],
    "phone_number": ["0000000000","9666666666","984563217","xxxxxxxxxx"],
    "date_of_birth": ["1950/09/13",datetime.date(2015,5,3)],
    "role": ['CC',"AT"],
    "status": ["PPP","FFF","ACT0"],
    }

class TestUserProfile(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('test')
        return super().setUp()
    def test_valid_data_set(self):
        valid_data=get_valid_profile_data()
        valid_data['user']=self.user
        profile=UserProfile.objects.create(**valid_data)
        for field, value in valid_data.items():
            with self.subTest(f'testing: {field}'):
                self.assertEqual(getattr(profile,field),value)
    def test_invalid_data(self):
        invalid_data=get_invalid_data()
        for field, values in invalid_data.items():
            for value in values:
                data=get_valid_profile_data()
                data['user']=self.user
                data[field]=value
                profile=UserProfile(**data)
                with self.subTest(field=field, value=value):
                    try:
                        profile.full_clean()
                        self.fail(F"{field}='{value}' should have raised Validation Error")
                    except ValidationError as e:
                        self.assertIn(field, e.error_dict)
                        for errors in e.error_dict[field]:
                            self.assertIn(errors.code,error_codes)
    
    def test_upload_profile_picture(self):
        dummy_image=get_dummy_image()
        data=get_valid_profile_data()
        data["profile_picture"]=dummy_image
        data["user"]=self.user
        profile=UserProfile.objects.create(**data)
        self.assertTrue(profile.profile_picture.name.endswith(".jpg"))

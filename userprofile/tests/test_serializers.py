from django.test import TestCase
from userprofile.serializers import CreateProfileSerializer
from userprofile import serializers 
import datetime
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from userprofile import choices
from rest_framework.exceptions import ValidationError


error_codes=[
    'max_length','invalid','blank','pattern',
    'ReservedWord','invalid_choice','UnderAge',
    'LargeFile', 'suspicious', 'invalid', 'unknown',
    'InvalidFormat','alpha',
]


def get_profile_data():
    return {
    "first_name": u"बिबेक",
    "last_name": "Ghimire",
    "display_name": "BIBEK",
    "email": "bibek2@example.com",
    "phone_number": "9840172373",
    "date_of_birth": datetime.date(2000, 5, 3),
    "role": "AD",
    "status": "ACT",
    }
def get_valid_data():
    return {
    "first_name": u"बिबेक",
    "last_name": "Ghimire",
    "display_name": "BIBEK",
    "email": "bibek@example.com",
    "phone_number": "9840172372",
    "date_of_birth": datetime.date(2000, 5, 3),
    "role": "ST",
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


class DummyRequest:
    def __init__(self,user):
        self.user=user

class TestUserProfile(TestCase):
    def setUp(self):
        aduser=User.objects.create_user('testadmin')
        adprofile_data=get_profile_data()
        adprofile_data['user']=aduser
        adprofile=UserProfile.objects.create(**adprofile_data)
        adprofile.save()
        request=DummyRequest(aduser)
        self.user=User.objects.create_user('test')
        self.context={
            'request':request
        }
        return super().setUp()
    
    def test_valid_data(self):
        valid_data=get_valid_data()
        valid_data['user']=self.user

        serializer=CreateProfileSerializer(data=valid_data,context=self.context)
        assert serializer.is_valid(),serializer.errors
        profile=serializer.save()
        assert profile.pk is not None
        for field,value in valid_data.items():
            with self.subTest(f'Testing: {field}'):
                self.assertEqual(getattr(profile,field),value)
        
    def test_invalid_data(self):
        invalid_data=get_invalid_data()
        for field, values in invalid_data.items():
            for value in values:
                data=get_valid_data()
                data[field]=value
                data['user']=self.user
                serializer=CreateProfileSerializer(data=data,context=self.context)
                with self.subTest(f'Testing: {field}'):
                    serializer.is_valid()
                    if serializer.is_valid():
                        self.fail(f'{field}="{value}" Should have raised Validation Error')
                    self.assertIn(field, serializer.errors)
                    for errors in serializer.errors[field]:
                        self.assertIn(errors.code, error_codes)


class TestListUserProfile(TestCase):
    def setUp(self):
        self.data=get_valid_data()
        self.data['user']=User.objects.create_user('testUser')
        self.profile=UserProfile.objects.create(**self.data)
        self.profile.save()
        self.data['email']='bibek3@example.com'
        self.data['phone_number']='9840172373'
        self.data['user']=User.objects.create_user('testUser2')
        self.profile=UserProfile.objects.create(**self.data)
        self.profile.save()
    def test_create_update(self):
        profiles=UserProfile.objects.all()
        serializer=serializers.ListProfileSerializer(profiles, many=True)
        with self.subTest("testing Create Fail"):
            self.data['email']='test@test.com'
            self.data['phone_number']='9856073273'
            self.data['user']=User.objects.create_user('testUser3')
            serializer=serializers.ListProfileSerializer(data=self.data)
            try:
                if serializer.is_valid():
                    serializer.save()
                    self.fail(f"saving method should have raised error")
                else:
                    raise ValidationError('must be valid')
            except ValidationError as e:
                self.assertIn('invalid',e.get_codes())
        with self.subTest("Testing Update Fail"):
            data={'email':'test3@test.com'}
            serializer=serializers.ListProfileSerializer(instance=self.profile,data=data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    self.fail("serializer should raise Error on Updating")
                except ValidationError as e:
                    self.assertIn('invalid', e.get_codes())
        
        with self.subTest("Testing Lists"):
            profiles=UserProfile.objects.all()
            serializer=serializers.ListProfileSerializer(profiles,many=True)
            print(serializer.data)


            




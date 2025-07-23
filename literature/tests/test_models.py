from django.test import TestCase
from literature.models import Chhanda, Poem, Gajal, Story
from userprofile.models import UserProfile
from django.contrib.auth.models import User
import datetime

def get_valid_data():
    return {
        'title':'मन्दाक्रान्ता',
        'character_count':17,
        'details':'''
यो छन्दमा 17 अक्षर रहने छन, 
यस छन्दमा

मगण SSS
भगण SII
नगण III
तगण SSI
तगण SSI
अन्त्यमा दुईटा गुरू SS
यसको लय यसरी तयार हुन्छः

नानानाना SSSS = ४
नननननना IIIIIS = ६
नाननानाननाना SISSISS = ७
'''
    }
def get_invalid_data(field_name):
    '''Returs the list of invalid data for field_name
    '''
    invalid_data={
        'title':[
            'hhue हुे huhrflja हुेजलजुहेुउक huefjkhafie iuerj iajuefh lajfue',
            '','***---***', 'युनिकोड र /*/-', 
        ],
        'character_count':[0,'पाँच'],
        'publish_status':[
            'DRAFT','','BCS','BC',
        ],
        'contributors':[
            'hhue हुे huhrflja हुेजलजुहेुउक huefjkhafie iuerj iajuefh lajfuehhue हुे huhrflja हुेजलजुहेुउक huefjkhafie iuerj iajuefh lajfuehhue हुे huhrflja हुेजलजुहेुउक huefjkhafie iuerj iajuefh lajfuehhue हुे huhrflja हुेजलजुहेुउक huefjkhafie iuerj iajuefh lajfuehhue हुे huhrflja हुेजलजुहेुउक huefjkhafie iuerj iajuefh lajfue',
            '',
        ],

    }
class TestChhanda(TestCase):
    def setUp(self):
        self.user1=User.objects.create_user(username='test1')
        self.user2=User.objects.create_user(username='test2')
        self.userprofile1=UserProfile.objects.create(**{
            "first_name": "Bibek",
            "last_name": "Ghimire",
            "display_name": "BIBEK",
            "email": "bibek@example.com",
            "phone_number": "9840172372",
            "date_of_birth": datetime.date(2000, 5, 3),
            "role": "AD",
            "status": "ACT",
            "user":self.user1
        })
        return super().setUp()
    def test_valid_data_set(self):
        valid_data=get_valid_data()
        valid_data['created_by']=self.userprofile1
        chhanda1=Chhanda.objects.create(**valid_data)
        for field,value in valid_data.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(chhanda1,field),value)
    # def test_invalid_data(self):
        
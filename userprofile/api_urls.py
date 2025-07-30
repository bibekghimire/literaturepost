from django.urls import path
from . import api_view


'''path('api/profiles/', include('userprofile.api_urls'))'''
app_name='userprofile'
urlpatterns=[
    path('list/', api_view.ProfileListView.as_view(), name='profile-list'),
    path('detail/<uuid:uuid>/', 
         api_view.ProfileDetailView.as_view(),
         name='profile-detail'),
    path('add_profile/',api_view.ProfileCreateView.as_view(),name='create-profile'),
    path('update-profile/',api_view.ProfileUpdateDeleteView.as_view(),name='delete-update'),
    path('add-user/',api_view.UserCreateView.as_view(),name='create-user'),
    path('listusers/',api_view.UserListView.as_view(),name='user-list'),
    path('updateusername/<uuid:uuid>/',api_view.UserNameUpdateView.as_view(), name='username-update'),
    path('resetpassword/<uuid:uuid>/',api_view.ResetPasswordView.as_view(),name='reset-password'),
    path('changepassword/<uuid:uuid>/',api_view.ChangePasswordView.as_view(),name='change-password'),
]


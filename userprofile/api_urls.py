from django.urls import path
from . import api_view


'''path('api/profiles/', include('userprofile.api_urls'))'''
app_name='userprofile'
urlpatterns=[
    path('list/', api_view.PublicProfileView.as_view(), name='public-profile'),
    path('<uuid:uuid>/',api_view.PublicProfileView.as_view(),name='userprofile-detail'),
    path('detail/<uuid:uuid>/', api_view.ProfileDetailUpdateView.as_view(),name='profile-detail-update'),
    path('detail/', api_view.ProfileDetailUpdateView.as_view(),name='profile-detail-update'),
    path('add-new/',api_view.ProfileCreateView.as_view(),name='create-profile'),
    path('add-user/',api_view.UserCreateView.as_view(),name='create-user'),
]

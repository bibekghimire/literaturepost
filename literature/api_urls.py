from django.urls import path
from . import api_views
'''path('api/literature/',include('literature.api_urls')),'''
app_name='literature'
urlpatterns=[
    # path('poem/add/',api_views.PoemCreateView.as_view(), name='add-poem'),
    # path('poem/all/',api_views.PoemListDetail.as_view(),name='all-poems'),
    # path('poem/<int:id>',api_views.PoemListDetail.as_view(),name='poem-detail'),
    # path('add/<str:type>/',api_views.LiteratureCreateView.as_view(),name='literature-create'),
    path('public/<str:type>/',api_views.LiteratureListCreateViews.as_view(),name='public-literature-list-create'),
    path('public/<str:type>/<int:id>/', api_views.LiteratureRetrieveUpdateDeleteView.as_view(),name='public-literature-details'),
    #self 
    path('user/<uuid:uuid>/<str:type>/',api_views.UserLiteratureListView.as_view(),name='user-literature-list-create'),
    # path('user/<uuid:uuid>/<str:type>/',api_views.UserLiteratureListView.as_view(),name='user-literature-list'),
    path('user/<uuid:uuid>/<str:type>/<int:id>/',api_views.UserLiteratureRetrieveUpdateDeleteView.as_view(), name='user-literature-details'),
    path('admin/<str:type>/all/',api_views.AdminLiteratureListView.as_view(),name='admin-all-literature'),
]

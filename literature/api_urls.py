from django.urls import path
from . import api_views
'''path('api/literature/',include('literature.api_urls')),'''
app_name='literature'
urlpatterns=[
    # path('poem/add/',api_views.PoemCreateView.as_view(), name='add-poem'),
    # path('poem/all/',api_views.PoemListDetail.as_view(),name='all-poems'),
    # path('poem/<int:id>',api_views.PoemListDetail.as_view(),name='poem-detail'),
    path('<str:type>/',api_views.LiteratureListCreateViews.as_view(),name='literature-list-create'),
    path('<str:type>/<int:id>/', api_views.LiteratureRetrieveUpdateDeleteView.as_view(),name='literature-details'),

]
from django.urls import path
from . import api_views

urlpatterns=[
    path('',api_views.ImportantPlacesListCreateView.as_view(),name='imp-places-list-create'),
    path('<str:type>/<int:id>', api_views.ImprotantPlacesRetrieveUpdateDeleteView.as_view(), name='retrieve-update-delete')
]
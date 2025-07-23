from django.urls import path
from .views import home_view, home

urlpatterns = [
    path('', home, name='all-home'),
    path('all/', home_view, name='home'),
]

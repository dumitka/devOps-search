from django.urls import path
from .views import search_accommodations

urlpatterns = [
    path('', search_accommodations),
]
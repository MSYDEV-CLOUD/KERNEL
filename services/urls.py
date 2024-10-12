# services/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ifta/', views.ifta_service_view, name='ifta_service'),
]

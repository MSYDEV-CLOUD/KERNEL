# news/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_home, name='news_home'),  # Make sure this matches the URL used in base.html
]

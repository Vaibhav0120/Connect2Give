from django.urls import path
from . import views

urlpatterns = [
    # This will be the main entry point to our app
    path('', views.index, name='index'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Web page URLs
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    
    # API URLs
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
]
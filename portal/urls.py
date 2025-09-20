from django.urls import path
from . import views

urlpatterns = [
    # Web page URLs
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/restaurant/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('dashboard/ngo/', views.ngo_dashboard, name='ngo_dashboard'),
    path('dashboard/volunteer/', views.volunteer_dashboard, name='volunteer_dashboard'),
    
    # Action URL for volunteers
    path('register_with_ngo/<int:ngo_id>/', views.register_with_ngo, name='register_with_ngo'),
    
    # API URLs
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
]
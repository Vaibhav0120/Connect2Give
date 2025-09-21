from django.urls import path
from . import views

urlpatterns = [
    # --- Main Site URLs ---
    path('', views.index, name='index'),
    path('register/step-1/', views.register_step_1, name='register_step_1'),
    path('register/step-2/', views.register_step_2, name='register_step_2'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- Dashboard URLs ---
    path('dashboard/restaurant/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('dashboard/volunteer/', views.volunteer_dashboard, name='volunteer_dashboard'),
    
    # --- NEW STRUCTURED NGO DASHBOARD URLS ---
    path('dashboard/ngo/', views.ngo_dashboard_overview, name='ngo_dashboard_overview'),
    path('dashboard/ngo/camps/', views.ngo_manage_camps, name='ngo_manage_camps'),
    path('dashboard/ngo/volunteers/', views.ngo_manage_volunteers, name='ngo_manage_volunteers'),
    path('dashboard/ngo/profile/', views.ngo_profile, name='ngo_profile'),
    path('dashboard/ngo/settings/', views.ngo_settings, name='ngo_settings'),

    # --- Action URLs ---
    path('register_with_ngo/<int:ngo_id>/', views.register_with_ngo, name='register_with_ngo'),
    path('donation/accept/<int:donation_id>/', views.accept_donation, name='accept_donation'),
    path('donation/collect/<int:donation_id>/', views.mark_as_collected, name='mark_as_collected'),
    path('donation/deliver/<int:donation_id>/', views.select_delivery_camp, name='select_delivery_camp'),
    path('donation/deliver/<int:donation_id>/to/<int:camp_id>/', views.mark_as_delivered, name='mark_as_delivered'),
    path('camp/complete/<int:camp_id>/', views.mark_camp_as_completed, name='mark_camp_as_completed'),
    path('donation/confirm_delivery/<int:donation_id>/', views.confirm_delivery, name='confirm_delivery'),

    # --- API URLs ---
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
]
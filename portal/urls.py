# portal/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Main Site & Auth URLs ---
    path('', views.index, name='index'),
    path('register/step-1/', views.register_step_1, name='register_step_1'),
    path('register/step-2/', views.register_step_2, name='register_step_2'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- Password Reset URLs ---
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt',
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # --- Google OAuth Callback ---
    path('accounts/google/login/callback/', views.google_callback, name='google_callback'),
    
    # --- Restaurant Dashboard URLs ---
    path('dashboard/restaurant/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('dashboard/restaurant/donations/', views.restaurant_donations, name='restaurant_donations'),
    path('dashboard/restaurant/profile/', views.restaurant_profile, name='restaurant_profile'),
    path('dashboard/restaurant/settings/', views.restaurant_settings, name='restaurant_settings'),

    # --- NGO Dashboard URLs ---
    path('dashboard/ngo/', views.ngo_dashboard_overview, name='ngo_dashboard_overview'),
    path('dashboard/ngo/camps/', views.ngo_manage_camps, name='ngo_manage_camps'),
    path('dashboard/ngo/volunteers/', views.ngo_manage_volunteers, name='ngo_manage_volunteers'),
    path('dashboard/ngo/profile/', views.ngo_profile, name='ngo_profile'),
    path('dashboard/ngo/settings/', views.ngo_settings, name='ngo_settings'),

    # --- Volunteer Dashboard URLs ---
    path('dashboard/volunteer/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('dashboard/volunteer/pickups/', views.volunteer_manage_pickups, name='volunteer_manage_pickups'),
    path('dashboard/volunteer/camps/', views.volunteer_manage_camps, name='volunteer_manage_camps'),
    path('dashboard/volunteer/profile/', views.volunteer_profile, name='volunteer_profile'),
    path('dashboard/volunteer/settings/', views.volunteer_settings, name='volunteer_settings'),
    
    # --- Action URLs ---
    path('register_with_ngo/<int:ngo_id>/', views.register_with_ngo, name='register_with_ngo'),
    path('unregister_from_ngo/<int:ngo_id>/', views.unregister_from_ngo, name='unregister_from_ngo'),
    path('donation/accept/<int:donation_id>/', views.accept_donation, name='accept_donation'),
    path('donation/deliver/to/<int:camp_id>/', views.mark_as_delivered, name='mark_as_delivered'),
    path('camp/complete/<int:camp_id>/', views.mark_camp_as_completed, name='mark_camp_as_completed'),
    path('donation/confirm_delivery/<int:donation_id>/', views.confirm_delivery, name='confirm_delivery'),

    # --- API URLs ---
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
]
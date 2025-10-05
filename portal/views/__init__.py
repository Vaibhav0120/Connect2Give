# portal/views/__init__.py

# Import all views from the separated files
from .auth_views import *
from .restaurant_views import *
from .ngo_views import *
from .volunteer_views import *
from .api_views import *

# --- HELPER & PUBLIC VIEWS ---
from django.shortcuts import render, redirect
import json
from ..models import User, DonationCamp, RestaurantProfile, Donation
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse


# FIX 1: Update this function to correctly redirect new users
def get_user_dashboard_redirect(user):
    if user.user_type == User.UserType.RESTAURANT:
        return redirect('restaurant_dashboard')
    elif user.user_type == User.UserType.NGO:
        return redirect('ngo_dashboard_overview')
    elif user.user_type == User.UserType.VOLUNTEER:
        return redirect('volunteer_dashboard')
    else:
        # For new users (default 'ADMIN' type), redirect to complete their profile
        return redirect('register_step_2')

def index(request):
    # FIX 2: Add this check at the top of the index view
    if request.user.is_authenticated:
        return get_user_dashboard_redirect(request.user)
        
    # The rest of the function is for non-logged-in users
    active_camps = DonationCamp.objects.filter(is_active=True).select_related('ngo')
    all_restaurants = RestaurantProfile.objects.filter(latitude__isnull=False, longitude__isnull=False)
    camps_map_data = [{"lat": c.latitude, "lon": c.longitude, "name": c.name, "ngo": c.ngo.ngo_name, "address": c.location_address, "start": c.start_time.strftime('%d %b %Y, %H:%M')} for c in active_camps if c.latitude and c.longitude]
    restaurants_map_data = [{"lat": r.latitude, "lon": r.longitude, "name": r.restaurant_name, "address": r.address} for r in all_restaurants]
    context = {'camps_map_data': json.dumps(camps_map_data), 'restaurants_map_data': json.dumps(restaurants_map_data)}
    return render(request, 'index.html', context)

# Action views used by multiple user types
@login_required(login_url='login_page')
def mark_camp_as_completed(request, camp_id):
    if request.user.user_type != 'NGO': return redirect('index')
    camp = get_object_or_404(DonationCamp, pk=camp_id, ngo=request.user.ngo_profile)
    if request.method == 'POST':
        camp.is_active = False
        camp.completed_at = timezone.now()
        camp.save()
    redirect_url = reverse('ngo_manage_camps') + '?view=history'
    return redirect(redirect_url)

@login_required(login_url='login_page')
def confirm_delivery(request, donation_id):
    if request.user.user_type != 'NGO': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, target_camp__ngo=request.user.ngo_profile)
    if request.method == 'POST':
        donation.status = 'DELIVERED'
        donation.save()
    redirect_url = reverse('ngo_manage_camps') + '?view=verification'
    return redirect(redirect_url)
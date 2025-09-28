from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from ..models import Donation, DonationCamp, RestaurantProfile
from ..forms import DonationForm, RestaurantProfileForm

@login_required(login_url='login_page')
def restaurant_dashboard(request):
    if request.user.user_type != 'RESTAURANT':
        return redirect('index')
    
    restaurant_profile = request.user.restaurant_profile
    stats = {
        'total_donations': Donation.objects.filter(restaurant=restaurant_profile).count(),
        'pending_donations': Donation.objects.filter(restaurant=restaurant_profile, status='PENDING').count(),
        'active_donations': Donation.objects.filter(restaurant=restaurant_profile, status__in=['ACCEPTED', 'COLLECTED']).count(),
        'completed_donations': Donation.objects.filter(restaurant=restaurant_profile, status='DELIVERED').count(),
    }
    
    active_camps = DonationCamp.objects.filter(is_active=True).select_related('ngo')
    camps_map_data = [
        {"lat": c.latitude, "lon": c.longitude, "name": c.name, "ngo": c.ngo.ngo_name, "address": c.location_address} 
        for c in active_camps if c.latitude and c.longitude
    ]
    
    context = {
        'stats': stats,
        'camps_map_data': json.dumps(camps_map_data)
    }
    return render(request, 'restaurant/dashboard.html', context)

@login_required(login_url='login_page')
def restaurant_donations(request):
    if request.user.user_type != 'RESTAURANT':
        return redirect('index')
    
    restaurant_profile = request.user.restaurant_profile
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.restaurant = restaurant_profile
            donation.save()
            messages.success(request, 'New donation posted successfully!')
            return redirect('restaurant_donations')
    else:
        form = DonationForm(initial={'pickup_address': restaurant_profile.address})
        
    donations = Donation.objects.filter(restaurant=restaurant_profile).order_by('-created_at')
    context = {
        'form': form, 
        'donations': donations,
        'default_address': restaurant_profile.address
    }
    return render(request, 'restaurant/donations.html', context)

@login_required(login_url='login_page')
def restaurant_profile(request):
    if request.user.user_type != 'RESTAURANT':
        return redirect('index')
    
    profile = get_object_or_404(RestaurantProfile, user=request.user)
    
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('restaurant_profile')
    else:
        form = RestaurantProfileForm(instance=profile)
        
    context = {'form': form}
    return render(request, 'restaurant/profile.html', context)

@login_required(login_url='login_page')
def restaurant_settings(request):
    if request.user.user_type != 'RESTAURANT':
        return redirect('index')
    return render(request, 'restaurant/settings.html')
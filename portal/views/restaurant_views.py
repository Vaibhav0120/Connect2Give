# portal/views/restaurant_views.py
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
            
            # Send webpush notifications to all volunteers with subscriptions
            try:
                from ..models import VolunteerProfile
                from pywebpush import webpush
                from django.conf import settings
                import json
                
                volunteers_with_subscription = VolunteerProfile.objects.exclude(
                    webpush_subscription__isnull=True
                ).exclude(webpush_subscription='')
                
                for volunteer in volunteers_with_subscription:
                    try:
                        subscription_info = json.loads(volunteer.webpush_subscription)
                        message_data = {
                            'title': 'New Donation Available! 🍱',
                            'body': f'{restaurant_profile.restaurant_name} posted: {donation.food_description}',
                            'url': '/dashboard/volunteer/pickups/'
                        }
                        
                        webpush(
                            subscription_info=subscription_info,
                            data=json.dumps(message_data),
                            vapid_private_key=settings.WEBPUSH_SETTINGS['VAPID_PRIVATE_KEY'],
                            vapid_claims={
                                "sub": f"mailto:{settings.WEBPUSH_SETTINGS['VAPID_ADMIN_EMAIL']}"
                            }
                        )
                    except Exception as e:
                        # Log error but don't break the flow
                        print(f"Failed to send notification to volunteer {volunteer.full_name}: {str(e)}")
            except Exception as e:
                # If webpush fails, just log it and continue
                print(f"Webpush error: {str(e)}")
            
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
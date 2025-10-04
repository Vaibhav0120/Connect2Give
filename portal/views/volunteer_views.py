# portal/views/volunteer_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
from ..models import Donation, DonationCamp, NGOProfile, VolunteerProfile
from ..forms import VolunteerProfileForm
from django.contrib import messages
from geopy.distance import geodesic

@login_required(login_url='login_page')
def volunteer_dashboard(request):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    
    volunteer_profile = request.user.volunteer_profile
    
    stats = {
        'active_pickups': Donation.objects.filter(assigned_volunteer=volunteer_profile, status__in=['ACCEPTED', 'COLLECTED']).count(),
        'completed_deliveries': Donation.objects.filter(assigned_volunteer=volunteer_profile, status='DELIVERED').count(),
        'registered_ngos': volunteer_profile.registered_ngos.count(),
        'available_donations': Donation.objects.filter(status='PENDING').count(),
    }

    available_donations = Donation.objects.filter(status='PENDING').select_related('restaurant').order_by('-created_at')
    upcoming_camps = DonationCamp.objects.filter(ngo__in=volunteer_profile.registered_ngos.all(), is_active=True).order_by('start_time')

    donations_map_data = [{"lat": d.restaurant.latitude, "lon": d.restaurant.longitude, "name": d.restaurant.restaurant_name, "food": d.food_description, "id": d.pk} for d in available_donations if d.restaurant.latitude and d.restaurant.longitude]
    camps_map_data = [{"lat": c.latitude, "lon": c.longitude, "name": c.name, "ngo": c.ngo.ngo_name, "address": c.location_address} for c in upcoming_camps if c.latitude and c.longitude]
    
    context = {
        'stats': stats,
        'donations_map_data': json.dumps(donations_map_data),
        'camps_map_data': json.dumps(camps_map_data)
    }
    return render(request, 'volunteer/dashboard.html', context)

@login_required(login_url='login_page')
def volunteer_manage_pickups(request):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    volunteer_profile = request.user.volunteer_profile
    
    thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
    Donation.objects.filter(status='ACCEPTED', accepted_at__lt=thirty_minutes_ago).update(status='PENDING', assigned_volunteer=None, accepted_at=None)

    active_donations = Donation.objects.filter(assigned_volunteer=volunteer_profile, status__in=['ACCEPTED', 'COLLECTED']).order_by('accepted_at')
    delivery_history = Donation.objects.filter(assigned_volunteer=volunteer_profile, status__in=['VERIFYING', 'DELIVERED']).order_by('-delivered_at')
    available_donations = Donation.objects.filter(status='PENDING').select_related('restaurant').order_by('-created_at')

    context = {
        'active_donations': active_donations,
        'available_donations': available_donations,
        'delivery_history': delivery_history,
        'view': request.GET.get('view')
    }

    if request.GET.get('view') == 'delivery_route':
        if not volunteer_profile.latitude or not volunteer_profile.longitude:
            messages.error(request, 'Please set your location in your profile before calculating routes.')
            return redirect('volunteer_profile')
        
        volunteer_location = (volunteer_profile.latitude, volunteer_profile.longitude)
        active_camps = DonationCamp.objects.filter(ngo__in=volunteer_profile.registered_ngos.all(), is_active=True)
        
        nearest_camp = None
        min_dist = float('inf')

        for camp in active_camps:
            if camp.latitude and camp.longitude:
                dist = geodesic(volunteer_location, (camp.latitude, camp.longitude)).km
                if dist < min_dist:
                    min_dist = dist
                    nearest_camp = camp
        
        context['nearest_camp'] = nearest_camp
        # --- FIX: Safely pass data to template ---
        if nearest_camp:
            context['nearest_camp_data'] = json.dumps({
                'name': nearest_camp.name,
                'latitude': nearest_camp.latitude,
                'longitude': nearest_camp.longitude,
                'pk': nearest_camp.pk
            })
        context['volunteer_location_data'] = json.dumps({
            'lat': volunteer_profile.latitude,
            'lon': volunteer_profile.longitude
        })
        # --- END FIX ---


    return render(request, 'volunteer/manage_pickups.html', context)


@login_required(login_url='login_page')
def volunteer_manage_camps(request):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    volunteer_profile = request.user.volunteer_profile
    registered_ngos = volunteer_profile.registered_ngos.all()
    
    context = {
        'registered_ngos': registered_ngos,
        'available_ngos': NGOProfile.objects.exclude(pk__in=[n.pk for n in registered_ngos]),
    }
    return render(request, 'volunteer/manage_camps.html', context)

@login_required(login_url='login_page')
def volunteer_profile(request):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
    
    profile = get_object_or_404(VolunteerProfile, user=request.user)
    if request.method == 'POST':
        form = VolunteerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('volunteer_profile')
    else:
        form = VolunteerProfileForm(instance=profile)
        
    context = {'form': form}
    return render(request, 'volunteer/profile.html', context)

@login_required(login_url='login_page')
def volunteer_settings(request):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    return render(request, 'volunteer/settings.html')


# --- ACTION VIEWS ---

@login_required(login_url='login_page')
def register_with_ngo(request, ngo_id):
    if request.user.user_type != 'VOLUNTEER' or request.method != 'POST': return redirect('index')
    ngo = get_object_or_404(NGOProfile, pk=ngo_id)
    volunteer = request.user.volunteer_profile
    ngo.volunteers.add(volunteer)
    messages.success(request, f"Successfully registered with {ngo.ngo_name}.")
    return redirect('volunteer_manage_camps')

@login_required(login_url='login_page')
def unregister_from_ngo(request, ngo_id):
    if request.user.user_type != 'VOLUNTEER' or request.method != 'POST': return redirect('index')
    ngo = get_object_or_404(NGOProfile, pk=ngo_id)
    volunteer = request.user.volunteer_profile
    ngo.volunteers.remove(volunteer)
    messages.success(request, f"Successfully unregistered from {ngo.ngo_name}.")
    return redirect('volunteer_manage_camps')

@login_required(login_url='login_page')
def accept_donation(request, donation_id):
    if request.user.user_type != 'VOLUNTEER' or request.method != 'POST': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id)
    volunteer = request.user.volunteer_profile

    if Donation.objects.filter(assigned_volunteer=volunteer, status__in=['ACCEPTED', 'COLLECTED']).count() >= 10:
        messages.error(request, 'You cannot accept more than 10 donations at a time.')
        return redirect('volunteer_manage_pickups')

    if donation.status == 'PENDING':
        donation.assigned_volunteer = volunteer
        donation.status = 'ACCEPTED'
        donation.accepted_at = timezone.now()
        donation.save()
        messages.success(request, 'Donation accepted. Please pick it up within 30 minutes.')
    else:
        messages.error(request, 'This donation is no longer available.')
    return redirect('volunteer_manage_pickups')

@login_required(login_url='login_page')
def mark_as_delivered(request, camp_id):
    if request.user.user_type != 'VOLUNTEER' or request.method != 'POST': return redirect('index')
    donations = Donation.objects.filter(assigned_volunteer=request.user.volunteer_profile, status__in=['ACCEPTED', 'COLLECTED'])
    camp = get_object_or_404(DonationCamp, pk=camp_id)
    
    updated_count = 0
    for donation in donations:
        donation.status = 'VERIFYING'
        donation.target_camp = camp
        donation.delivered_at = timezone.now()
        donation.save()
        updated_count += 1
        
    if updated_count > 0:
        messages.success(request, f'{updated_count} item(s) marked as delivered and are pending verification by the NGO.')
    else:
        messages.warning(request, 'You had no active pickups to deliver.')

    return redirect('volunteer_manage_pickups')
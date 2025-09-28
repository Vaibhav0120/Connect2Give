# portal/views/volunteer_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
from ..models import Donation, DonationCamp, NGOProfile, VolunteerProfile

@login_required(login_url='login_page')
def volunteer_dashboard(request):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    volunteer_profile = request.user.volunteer_profile
    registered_ngos = volunteer_profile.registered_ngos.all()
    thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
    Donation.objects.filter(status='ACCEPTED', accepted_at__lt=thirty_minutes_ago).update(status='PENDING', assigned_volunteer=None, accepted_at=None)
    my_active_donations = Donation.objects.filter(assigned_volunteer=volunteer_profile, status__in=['ACCEPTED', 'COLLECTED']).order_by('accepted_at')
    delivery_history = Donation.objects.filter(assigned_volunteer=volunteer_profile, status__in=['VERIFYING', 'DELIVERED']).order_by('-delivered_at')
    available_donations = Donation.objects.filter(status='PENDING').select_related('restaurant').order_by('-created_at')
    
    upcoming_camps = DonationCamp.objects.filter(ngo__in=registered_ngos, is_active=True).order_by('start_time')

    donations_map_data = [{"lat": d.restaurant.latitude, "lon": d.restaurant.longitude, "name": d.restaurant.restaurant_name, "food": d.food_description, "pickup_address": d.pickup_address, "id": d.pk} for d in available_donations if d.restaurant.latitude and d.restaurant.longitude]
    camps_map_data = [{"lat": c.latitude, "lon": c.longitude, "name": c.name, "ngo": c.ngo.ngo_name, "address": c.location_address} for c in upcoming_camps if c.latitude and c.longitude]
    context = {
        'registered_ngos': registered_ngos,
        'available_ngos': NGOProfile.objects.exclude(pk__in=[n.pk for n in registered_ngos]),
        'camps': upcoming_camps,
        'available_donations': available_donations,
        'my_active_donations': my_active_donations,
        'delivery_history': delivery_history,
        'donations_map_data': json.dumps(donations_map_data),
        'camps_map_data': json.dumps(camps_map_data)
    }
    return render(request, 'volunteer/dashboard.html', context)

@login_required(login_url='login_page')
def register_with_ngo(request, ngo_id):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    ngo = get_object_or_404(NGOProfile, pk=ngo_id)
    volunteer = request.user.volunteer_profile
    ngo.volunteers.add(volunteer)
    return redirect('volunteer_dashboard')

@login_required(login_url='login_page')
def accept_donation(request, donation_id):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id)
    volunteer = request.user.volunteer_profile
    if donation.status == 'PENDING':
        donation.assigned_volunteer = volunteer
        donation.status = 'ACCEPTED'
        donation.accepted_at = timezone.now()
        donation.save()
    return redirect('volunteer_dashboard')

@login_required(login_url='login_page')
def mark_as_collected(request, donation_id):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, assigned_volunteer=request.user.volunteer_profile)
    donation.status = 'COLLECTED'
    donation.collected_at = timezone.now()
    donation.save()
    return redirect('select_delivery_camp', donation_id=donation.pk)

@login_required(login_url='login_page')
def select_delivery_camp(request, donation_id):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, assigned_volunteer=request.user.volunteer_profile)
    volunteer_profile = request.user.volunteer_profile
    registered_ngos = volunteer_profile.registered_ngos.all()
    active_camps = DonationCamp.objects.filter(ngo__in=registered_ngos, is_active=True).order_by('start_time')
    context = {'donation': donation, 'camps': active_camps}
    return render(request, 'volunteer/select_camp.html', context)

@login_required(login_url='login_page')
def mark_as_delivered(request, donation_id, camp_id):
    if request.user.user_type != 'VOLUNTEER': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, assigned_volunteer=request.user.volunteer_profile)
    camp = get_object_or_404(DonationCamp, pk=camp_id)
    donation.status = 'VERIFYING'
    donation.target_camp = camp
    donation.delivered_at = timezone.now()
    donation.save()
    return redirect('volunteer_dashboard')
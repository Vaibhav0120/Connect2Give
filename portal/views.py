# portal/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from django.contrib import messages
import json
import os 
from django.conf import settings 

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer
from .models import User, RestaurantProfile, NGOProfile, VolunteerProfile, DonationCamp, Donation
from .forms import DonationCampForm, DonationForm, NGOProfileForm, RestaurantProfileForm

# --- HELPER & PUBLIC VIEWS ---
def get_user_dashboard_redirect(user):
    if user.user_type == User.UserType.RESTAURANT: return redirect('restaurant_dashboard')
    elif user.user_type == User.UserType.NGO: return redirect('ngo_dashboard_overview')
    elif user.user_type == User.UserType.VOLUNTEER: return redirect('volunteer_dashboard')
    else: return redirect('index')

def index(request):
    active_camps = DonationCamp.objects.filter(is_active=True).select_related('ngo')
    all_restaurants = RestaurantProfile.objects.filter(latitude__isnull=False, longitude__isnull=False)
    camps_map_data = [{"lat": c.latitude, "lon": c.longitude, "name": c.name, "ngo": c.ngo.ngo_name, "address": c.location_address, "start": c.start_time.strftime('%d %b %Y, %H:%M')} for c in active_camps if c.latitude and c.longitude]
    restaurants_map_data = [{"lat": r.latitude, "lon": r.longitude, "name": r.restaurant_name, "address": r.address} for r in all_restaurants]
    context = {'camps_map_data': json.dumps(camps_map_data), 'restaurants_map_data': json.dumps(restaurants_map_data)}
    return render(request, 'index.html', context)

# --- AUTH VIEWS ---
def register_step_1(request):
    if request.user.is_authenticated: return get_user_dashboard_redirect(request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists(): 
            return render(request, 'auth/register_step_1.html', {'error': 'Username already exists.'})
        if User.objects.filter(email=email).exists(): 
            return render(request, 'auth/register_step_1.html', {'error': 'Email already registered.'})
        request.session['registration_data'] = {'username': username, 'email': email, 'password': request.POST.get('password'), 'user_type': request.POST.get('user_type')}
        return redirect('register_step_2')
    return render(request, 'auth/register_step_1.html')

def register_step_2(request):
    if request.user.is_authenticated: return get_user_dashboard_redirect(request.user)
    registration_data = request.session.get('registration_data')
    if not registration_data: return redirect('register_step_1')
    user_type = registration_data.get('user_type')
    if request.method == 'POST':
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        address = request.POST.get('address')
        user = User.objects.create_user(username=registration_data['username'], email=registration_data['email'], password=registration_data['password'], user_type=user_type)
        if user_type == User.UserType.RESTAURANT:
            RestaurantProfile.objects.create(user=user, restaurant_name=request.POST.get('restaurant_name'), address=address, phone_number=request.POST.get('restaurant_phone_number'), latitude=latitude, longitude=longitude)
        elif user_type == User.UserType.NGO:
            NGOProfile.objects.create(user=user, ngo_name=request.POST.get('ngo_name'), registration_number=request.POST.get('registration_number'), address=address, contact_person=request.POST.get('contact_person'), latitude=latitude, longitude=longitude)
        elif user_type == User.UserType.VOLUNTEER:
            VolunteerProfile.objects.create(user=user, full_name=request.POST.get('full_name'), phone_number=request.POST.get('phone_number'), skills=request.POST.get('skills'), address=address, latitude=latitude, longitude=longitude)
        del request.session['registration_data']
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login_page')
    context = {'user_type': user_type}
    return render(request, 'auth/register_step_2.html', context)

def login_page(request):
    if request.user.is_authenticated: return get_user_dashboard_redirect(request.user)
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return get_user_dashboard_redirect(user)
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

# --- RESTAURANT DASHBOARD VIEWS ---
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
    
    # Fetch all active camps to display on the map
    active_camps = DonationCamp.objects.filter(is_active=True).select_related('ngo')
    camps_map_data = [
        {
            "lat": c.latitude, 
            "lon": c.longitude, 
            "name": c.name, 
            "ngo": c.ngo.ngo_name, 
            "address": c.location_address
        } 
        for c in active_camps if c.latitude and c.longitude
    ]
    
    context = {
        'stats': stats,
        'camps_map_data': json.dumps(camps_map_data) # Pass map data to the template
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
        old_profile_pic_path = profile.profile_picture.path if profile.profile_picture else None
        
        form = RestaurantProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save()

            if old_profile_pic_path and updated_profile.profile_picture and old_profile_pic_path != updated_profile.profile_picture.path:
                if os.path.exists(old_profile_pic_path):
                    os.remove(old_profile_pic_path)
            
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

# --- NGO DASHBOARD VIEWS ---
@login_required(login_url='login_page')
def ngo_dashboard_overview(request):
    if request.user.user_type != 'NGO': return redirect('index')
    ngo_profile = request.user.ngo_profile
    stats = {'active_camps': DonationCamp.objects.filter(ngo=ngo_profile, is_active=True).count(), 'total_volunteers': ngo_profile.volunteers.count(), 'donations_to_verify': Donation.objects.filter(target_camp__ngo=ngo_profile, status='VERIFYING').count(), 'total_donations_received': Donation.objects.filter(target_camp__ngo=ngo_profile, status='DELIVERED').count()}
    context = {'stats': stats}
    return render(request, 'ngo/dashboard_overview.html', context)

@login_required(login_url='login_page')
def ngo_manage_camps(request):
    if request.user.user_type != 'NGO': return redirect('index')
    ngo_profile = request.user.ngo_profile
    if request.method == 'POST':
        form = DonationCampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.ngo = ngo_profile
            camp.save()
            messages.success(request, 'New camp created successfully!')
            return redirect('ngo_manage_camps')
    else:
        form = DonationCampForm()
    active_camps = DonationCamp.objects.filter(ngo=ngo_profile, is_active=True).order_by('start_time')
    completed_camps = DonationCamp.objects.filter(ngo=ngo_profile, is_active=False).order_by('-completed_at')
    donations_to_verify = Donation.objects.filter(target_camp__ngo=ngo_profile, status='VERIFYING').order_by('delivered_at')
    context = {'form': form, 'active_camps': active_camps, 'completed_camps': completed_camps, 'donations_to_verify': donations_to_verify}
    return render(request, 'ngo/manage_camps.html', context)

@login_required(login_url='login_page')
def ngo_manage_volunteers(request):
    if request.user.user_type != 'NGO': return redirect('index')
    ngo_profile = request.user.ngo_profile
    registered_volunteers = ngo_profile.volunteers.annotate(active_deliveries=Count('assigned_donations', filter=Q(assigned_donations__status__in=['ACCEPTED', 'COLLECTED']))).order_by('full_name')
    context = {'volunteers': registered_volunteers}
    return render(request, 'ngo/manage_volunteers.html', context)

@login_required(login_url='login_page')
def ngo_profile(request):
    if request.user.user_type != 'NGO':
        return redirect('index')
    
    profile = get_object_or_404(NGOProfile, user=request.user)

    if request.method == 'POST':
        old_profile_pic_path = profile.profile_picture.path if profile.profile_picture else None
        old_banner_image_path = profile.banner_image.path if profile.banner_image else None
        
        form = NGOProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save()

            if old_profile_pic_path and updated_profile.profile_picture and old_profile_pic_path != updated_profile.profile_picture.path:
                if os.path.exists(old_profile_pic_path):
                    os.remove(old_profile_pic_path)
            
            if old_banner_image_path and updated_profile.banner_image and old_banner_image_path != updated_profile.banner_image.path:
                if os.path.exists(old_banner_image_path):
                    os.remove(old_banner_image_path)

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('ngo_profile')
    else:
        form = NGOProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'ngo/profile.html', context)

@login_required(login_url='login_page')
def ngo_settings(request):
    if request.user.user_type != 'NGO': return redirect('index')
    return render(request, 'ngo/settings.html')

# --- VOLUNTEER DASHBOARD AND ACTIONS ---
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
    context = {'registered_ngos': registered_ngos, 'available_ngos': NGOProfile.objects.exclude(pk__in=[n.pk for n in registered_ngos]), 'camps': upcoming_camps, 'available_donations': available_donations, 'my_active_donations': my_active_donations, 'delivery_history': delivery_history, 'donations_map_data': json.dumps(donations_map_data), 'camps_map_data': json.dumps(camps_map_data)}
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

@login_required(login_url='login_page')
def mark_camp_as_completed(request, camp_id):
    if request.user.user_type != 'NGO': return redirect('index')
    camp = get_object_or_404(DonationCamp, pk=camp_id, ngo=request.user.ngo_profile)
    if request.method == 'POST':
        camp.is_active = False
        camp.completed_at = timezone.now()
        camp.save()
    return redirect('ngo_manage_camps')

@login_required(login_url='login_page')
def confirm_delivery(request, donation_id):
    if request.user.user_type != 'NGO': return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, target_camp__ngo=request.user.ngo_profile)
    if request.method == 'POST':
        donation.status = 'DELIVERED'
        donation.save()
    return redirect('ngo_manage_camps')

# --- API VIEWS ---
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # Pylance flags this because it can't statically determine that the '.user' 
        # attribute exists. In DRF's AuthTokenSerializer, it's guaranteed to exist 
        # after a successful .is_valid() call. We use 'type: ignore' to acknowledge this.
        user = serializer.user # type: ignore
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk, 'user_type': user.user_type})
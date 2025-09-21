from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer
from .models import User, RestaurantProfile, NGOProfile, VolunteerProfile, DonationCamp, Donation
from .forms import DonationCampForm, DonationForm

# --- Helper Function for Redirection ---

def get_user_dashboard_redirect(user):
    """
    Determines the correct redirect path based on the user's type.
    """
    if user.user_type == User.UserType.RESTAURANT:
        return redirect('restaurant_dashboard')
    elif user.user_type == User.UserType.NGO:
        return redirect('ngo_dashboard')
    elif user.user_type == User.UserType.VOLUNTEER:
        return redirect('volunteer_dashboard')
    else: # This handles the ADMIN type
        return redirect('index')

# --- Web Page Views ---

def index(request):
    """Renders the main homepage."""
    return render(request, 'index.html')

def register_page(request):
    """Handles the user registration form submission."""
    if request.user.is_authenticated:
        return get_user_dashboard_redirect(request.user)

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user = User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=request.POST.get('password'),
            user_type=user_type
        )
        if user_type == User.UserType.RESTAURANT:
            RestaurantProfile.objects.create(user=user, restaurant_name=request.POST.get('restaurant_name'), address=request.POST.get('restaurant_address'), phone_number=request.POST.get('restaurant_phone_number'))
        elif user_type == User.UserType.NGO:
            NGOProfile.objects.create(user=user, ngo_name=request.POST.get('ngo_name'), registration_number=request.POST.get('registration_number'), address=request.POST.get('address'), contact_person=request.POST.get('contact_person'))
        elif user_type == User.UserType.VOLUNTEER:
            VolunteerProfile.objects.create(user=user, full_name=request.POST.get('full_name'), phone_number=request.POST.get('phone_number'), skills=request.POST.get('skills'))
        
        login(request, user)
        return get_user_dashboard_redirect(user)
    return render(request, 'register.html')

def login_page(request):
    """Handles the user login form submission."""
    if request.user.is_authenticated:
        return get_user_dashboard_redirect(request.user)

    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return get_user_dashboard_redirect(user)
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')

def logout_view(request):
    """Logs the user out and redirects to the homepage."""
    logout(request)
    return redirect('index')

# --- Dashboard Views ---

@login_required(login_url='login_page')
def restaurant_dashboard(request):
    if request.user.user_type != 'RESTAURANT':
        return redirect('index')
    restaurant_profile = request.user.restaurant_profile
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.restaurant = restaurant_profile
            donation.save()
            return redirect('restaurant_dashboard')
    else:
        form = DonationForm()
    donations = Donation.objects.filter(restaurant=restaurant_profile).order_by('-created_at')
    context = {'form': form, 'donations': donations}
    return render(request, 'restaurant_dashboard.html', context)

@login_required(login_url='login_page')
def ngo_dashboard(request):
    if request.user.user_type != 'NGO':
        return redirect('index')
    ngo_profile = request.user.ngo_profile
    if request.method == 'POST' and 'create_camp' in request.POST:
        form = DonationCampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.ngo = ngo_profile
            camp.save()
            return redirect('ngo_dashboard')
    else:
        form = DonationCampForm()
    active_camps = DonationCamp.objects.filter(ngo=ngo_profile, is_active=True).order_by('start_time')
    completed_camps = DonationCamp.objects.filter(ngo=ngo_profile, is_active=False).order_by('-completed_at')
    registered_volunteers = ngo_profile.volunteers.all()
    donations_to_verify = Donation.objects.filter(target_camp__ngo=ngo_profile, status='VERIFYING').order_by('delivered_at')
    context = {
        'form': form,
        'active_camps': active_camps,
        'completed_camps': completed_camps,
        'volunteers': registered_volunteers,
        'donations_to_verify': donations_to_verify,
    }
    return render(request, 'ngo_dashboard.html', context)

@login_required(login_url='login_page')
def volunteer_dashboard(request):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
        
    volunteer_profile = request.user.volunteer_profile 
    registered_ngos = volunteer_profile.registered_ngos.all()
    
    thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
    Donation.objects.filter(status='ACCEPTED', accepted_at__lt=thirty_minutes_ago).update(status='PENDING', assigned_volunteer=None, accepted_at=None)
    available_donations = Donation.objects.filter(status='PENDING').order_by('-created_at')
    my_active_donations = Donation.objects.filter(assigned_volunteer=volunteer_profile, status__in=['ACCEPTED', 'COLLECTED']).order_by('accepted_at')
    
    delivery_history = Donation.objects.filter(
        assigned_volunteer=volunteer_profile,
        status__in=['VERIFYING', 'DELIVERED']
    ).order_by('-delivered_at')
    
    registered_ngo_pks = [ngo.pk for ngo in registered_ngos]
    available_ngos = NGOProfile.objects.exclude(pk__in=registered_ngo_pks)
    upcoming_camps = DonationCamp.objects.filter(ngo__in=registered_ngos, is_active=True).order_by('start_time')
    
    context = {
        'registered_ngos': registered_ngos,
        'available_ngos': available_ngos,
        'camps': upcoming_camps,
        'available_donations': available_donations,
        'my_active_donations': my_active_donations,
        'delivery_history': delivery_history,
    }
    return render(request, 'volunteer_dashboard.html', context)

# --- Action Views ---

@login_required(login_url='login_page')
def register_with_ngo(request, ngo_id):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
    ngo = get_object_or_404(NGOProfile, pk=ngo_id)
    volunteer = request.user.volunteer_profile
    ngo.volunteers.add(volunteer)
    return redirect('volunteer_dashboard')

@login_required(login_url='login_page')
def accept_donation(request, donation_id):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
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
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, assigned_volunteer=request.user.volunteer_profile)
    donation.status = 'COLLECTED'
    donation.collected_at = timezone.now()
    donation.save()
    return redirect('select_delivery__camp', donation_id=donation.pk)

@login_required(login_url='login_page')
def select_delivery_camp(request, donation_id):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, assigned_volunteer=request.user.volunteer_profile)
    volunteer_profile = request.user.volunteer_profile
    registered_ngos = volunteer_profile.registered_ngos.all()
    active_camps = DonationCamp.objects.filter(ngo__in=registered_ngos, is_active=True).order_by('start_time')
    context = {'donation': donation, 'camps': active_camps}
    return render(request, 'select_camp.html', context)

@login_required(login_url='login_page')
def mark_as_delivered(request, donation_id, camp_id):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, assigned_volunteer=request.user.volunteer_profile)
    camp = get_object_or_404(DonationCamp, pk=camp_id)
    donation.status = 'VERIFYING'
    donation.target_camp = camp
    donation.delivered_at = timezone.now()
    donation.save()
    return redirect('volunteer_dashboard')

@login_required(login_url='login_page')
def mark_camp_as_completed(request, camp_id):
    if request.user.user_type != 'NGO':
        return redirect('index')
    camp = get_object_or_404(DonationCamp, pk=camp_id, ngo=request.user.ngo_profile)
    if request.method == 'POST':
        camp.is_active = False
        camp.completed_at = timezone.now()
        camp.save()
    return redirect('ngo_dashboard')

@login_required(login_url='login_page')
def confirm_delivery(request, donation_id):
    if request.user.user_type != 'NGO':
        return redirect('index')
    donation = get_object_or_404(Donation, pk=donation_id, target_camp__ngo=request.user.ngo_profile)
    if request.method == 'POST':
        donation.status = 'DELIVERED'
        donation.save()
    return redirect('ngo_dashboard')

# --- API Views (for future JavaScript frontend) ---
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
class LoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.user # type: ignore
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk, 'user_type': user.user_type})
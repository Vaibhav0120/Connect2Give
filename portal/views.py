from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer
from .models import User, RestaurantProfile, NGOProfile, VolunteerProfile, DonationCamp
from .forms import DonationCampForm

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
    return render(request, 'restaurant_dashboard.html')

@login_required(login_url='login_page')
def ngo_dashboard(request):
    if request.user.user_type != 'NGO':
        return redirect('index')
    ngo_profile = request.user.ngo_profile
    if request.method == 'POST':
        form = DonationCampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.ngo = ngo_profile
            camp.save()
            return redirect('ngo_dashboard')
    else:
        form = DonationCampForm()
    camps = DonationCamp.objects.filter(ngo=ngo_profile).order_by('-created_at')
    registered_volunteers = ngo_profile.volunteers.all()
    context = {
        'form': form,
        'camps': camps,
        'volunteers': registered_volunteers
    }
    return render(request, 'ngo_dashboard.html', context)

@login_required(login_url='login_page')
def volunteer_dashboard(request):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
        
    # THE TYPO IS FIXED HERE (volunteer__profile -> volunteer_profile)
    volunteer_profile = request.user.volunteer_profile 
    
    registered_ngos = volunteer_profile.registered_ngos.all()
    registered_ngo_pks = [ngo.pk for ngo in registered_ngos]
    available_ngos = NGOProfile.objects.exclude(pk__in=registered_ngo_pks)
    upcoming_camps = DonationCamp.objects.filter(ngo__in=registered_ngos, is_active=True).order_by('start_time')
    context = {
        'registered_ngos': registered_ngos,
        'available_ngos': available_ngos,
        'camps': upcoming_camps,
    }
    return render(request, 'volunteer_dashboard.html', context)

@login_required(login_url='login_page')
def register_with_ngo(request, ngo_id):
    if request.user.user_type != 'VOLUNTEER':
        return redirect('index')
    ngo = get_object_or_404(NGOProfile, pk=ngo_id)
    volunteer = request.user.volunteer_profile
    ngo.volunteers.add(volunteer)
    return redirect('volunteer_dashboard')

# --- API Views ---
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


# portal/views/auth_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from ..models import User, RestaurantProfile, NGOProfile, VolunteerProfile

def get_user_dashboard_redirect(user):
    if user.user_type == User.UserType.RESTAURANT:
        return redirect('restaurant_dashboard')
    elif user.user_type == User.UserType.NGO:
        return redirect('ngo_dashboard_overview')
    elif user.user_type == User.UserType.VOLUNTEER:
        return redirect('volunteer_dashboard')
    else:
        return redirect('index')

def register_step_1(request):
    if request.user.is_authenticated:
        return get_user_dashboard_redirect(request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register_step_1.html', {'error': 'Username already exists.'})
        if User.objects.filter(email=email).exists():
            return render(request, 'auth/register_step_1.html', {'error': 'Email already registered.'})
        request.session['registration_data'] = {
            'username': username,
            'email': email,
            'password': request.POST.get('password'),
            'user_type': request.POST.get('user_type')
        }
        return redirect('register_step_2')
    return render(request, 'auth/register_step_1.html')

def register_step_2(request):
    if request.user.is_authenticated:
        return get_user_dashboard_redirect(request.user)
    registration_data = request.session.get('registration_data')
    if not registration_data:
        return redirect('register_step_1')
    user_type = registration_data.get('user_type')
    if request.method == 'POST':
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        address = request.POST.get('address')
        user = User.objects.create_user(
            username=registration_data['username'],
            email=registration_data['email'],
            password=registration_data['password'],
            user_type=user_type
        )
        if user_type == User.UserType.RESTAURANT:
            RestaurantProfile.objects.create(
                user=user,
                restaurant_name=request.POST.get('restaurant_name'),
                address=address,
                phone_number=request.POST.get('restaurant_phone_number'),
                latitude=latitude,
                longitude=longitude
            )
        elif user_type == User.UserType.NGO:
            NGOProfile.objects.create(
                user=user,
                ngo_name=request.POST.get('ngo_name'),
                registration_number=request.POST.get('registration_number'),
                address=address,
                contact_person=request.POST.get('contact_person'),
                latitude=latitude,
                longitude=longitude
            )
        elif user_type == User.UserType.VOLUNTEER:
            VolunteerProfile.objects.create(
                user=user,
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                skills=request.POST.get('skills'),
                address=address,
                latitude=latitude,
                longitude=longitude
            )
        del request.session['registration_data']
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login_page')
    context = {'user_type': user_type}
    return render(request, 'auth/register_step_2.html', context)

def login_page(request):
    if request.user.is_authenticated:
        return get_user_dashboard_redirect(request.user)
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

def google_callback(request):
    """Handle Google OAuth callback"""
    if request.user.is_authenticated:
        # Check if user has a user_type set
        if request.user.user_type == User.UserType.ADMIN:
            # User needs to select a type
            return redirect('google_select_user_type')
        return get_user_dashboard_redirect(request.user)
    return redirect('login_page')

def google_select_user_type(request):
    """Allow Google OAuth users to select their user type"""
    if not request.user.is_authenticated:
        return redirect('login_page')
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type in [User.UserType.RESTAURANT, User.UserType.NGO, User.UserType.VOLUNTEER]:
            request.user.user_type = user_type
            request.user.save()
            
            # Create profile based on user type
            if user_type == User.UserType.RESTAURANT and not hasattr(request.user, 'restaurant_profile'):
                RestaurantProfile.objects.create(
                    user=request.user,
                    restaurant_name=request.user.get_full_name() or request.user.username,
                    address='',
                    phone_number=''
                )
            elif user_type == User.UserType.NGO and not hasattr(request.user, 'ngo_profile'):
                NGOProfile.objects.create(
                    user=request.user,
                    ngo_name=request.user.get_full_name() or request.user.username,
                    registration_number='',
                    address='',
                    contact_person=request.user.get_full_name() or request.user.username
                )
            elif user_type == User.UserType.VOLUNTEER and not hasattr(request.user, 'volunteer_profile'):
                VolunteerProfile.objects.create(
                    user=request.user,
                    full_name=request.user.get_full_name() or request.user.username,
                )
            
            messages.success(request, 'Profile created successfully! Please complete your profile information.')
            return get_user_dashboard_redirect(request.user)
    
    return render(request, 'auth/google_select_user_type.html')
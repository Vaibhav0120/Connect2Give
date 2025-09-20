from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer
from .models import User, NGOProfile, VolunteerProfile

# --- Web Page Views ---

def index(request):
    return render(request, 'index.html')

def register_page(request):
    if request.method == 'POST':
        # Extract data from the form
        user_type = request.POST.get('user_type')
        
        # Create the user
        user = User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=request.POST.get('password'),
            user_type=user_type
        )
        
        # Create the corresponding profile
        if user_type == User.UserType.NGO:
            NGOProfile.objects.create(
                user=user,
                ngo_name=request.POST.get('ngo_name'),
                registration_number=request.POST.get('registration_number'),
                address=request.POST.get('address'),
                contact_person=request.POST.get('contact_person')
            )
        elif user_type == User.UserType.VOLUNTEER:
            VolunteerProfile.objects.create(
                user=user,
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                skills=request.POST.get('skills')
            )
        
        # Log the user in and redirect them
        login(request, user)
        return redirect('index') # Redirect to the homepage after registration

    return render(request, 'register.html')

def login_page(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user is not None:
            login(request, user)
            return redirect('index') # Redirect to homepage on successful login
        else:
            # Handle invalid login here (e.g., show an error message)
            return render(request, 'login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'login.html')

# --- API Views ---

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # (Logic is handled by the serializer)

class LoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # CORRECTED LINE: Access the user from the serializer attribute directly
        user = serializer.user # type: ignore
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'user_type': user.user_type
        })


from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """
    Custom User model to handle different roles within the application.
    Inherits from Django's AbstractUser to leverage built-in authentication.
    """
    class UserType(models.TextChoices):
        NGO = 'NGO', 'NGO'
        VOLUNTEER = 'VOLUNTEER', 'Volunteer'
        DONOR = 'DONOR', 'Donor'

    # The first value is stored in the DB, the second is for human-readable display.
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.DONOR)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})" # type: ignore


class NGOProfile(models.Model):
    """
    Profile model to store additional information for users of type NGO.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='ngo_profile')
    ngo_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ngo_name


class VolunteerProfile(models.Model):
    """
    Profile model to store additional information for users of type VOLUNTEER.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='volunteer_profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Driving, Cooking, Medical")
    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


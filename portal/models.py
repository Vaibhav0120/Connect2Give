from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- CORE USER AND PROFILE MODELS ---
class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        RESTAURANT = 'RESTAURANT', 'Restaurant'
        NGO = 'NGO', 'NGO'
        VOLUNTEER = 'VOLUNTEER', 'Volunteer'
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.ADMIN)
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})" # type: ignore

class RestaurantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='restaurant_profile')
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/restaurants/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.restaurant_name

class VolunteerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='volunteer_profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Driving, Cooking, Medical")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/volunteers/', null=True, blank=True)
    webpush_subscription = models.TextField(blank=True, null=True, help_text="Web push subscription data (JSON)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.full_name

class NGOProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='ngo_profile')
    ngo_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    contact_person = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/ngos/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='banner_images/ngos/', null=True, blank=True)
    volunteers = models.ManyToManyField('VolunteerProfile', through='NGOVolunteer', related_name='registered_ngos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.ngo_name

class NGOVolunteer(models.Model):
    ngo = models.ForeignKey(NGOProfile, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('ngo', 'volunteer')
    def __str__(self):
        return f"{self.volunteer.full_name} is a volunteer for {self.ngo.ngo_name}"

class DonationCamp(models.Model):
    ngo = models.ForeignKey(NGOProfile, on_delete=models.CASCADE, related_name='camps')
    name = models.CharField(max_length=255)
    location_address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    start_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.name} by {self.ngo.ngo_name}"

class Donation(models.Model):
    class DonationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Pickup'
        ACCEPTED = 'ACCEPTED', 'On its Way'
        COLLECTED = 'COLLECTED', 'Collected by Volunteer'
        VERIFYING = 'VERIFYING', 'Pending Verification'
        DELIVERED = 'DELIVERED', 'Delivered & Verified'

    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    restaurant = models.ForeignKey(RestaurantProfile, on_delete=models.CASCADE, related_name='donations')
    food_description = models.CharField(max_length=255, help_text="e.g., 20 veg thalis, 5kg rice")
    quantity = models.PositiveIntegerField(help_text="e.g., number of meals, weight in kg")
    pickup_address = models.TextField()
    status = models.CharField(max_length=10, choices=DonationStatus.choices, default=DonationStatus.PENDING, db_index=True)
    assigned_volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_donations', db_index=True)
    target_camp = models.ForeignKey(DonationCamp, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations_received', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Rating and Review fields
    rating = models.IntegerField(null=True, blank=True, choices=RATING_CHOICES, help_text="Rating from 1 to 5 stars")
    review = models.TextField(null=True, blank=True, help_text="NGO's review of the volunteer delivery")

    def __str__(self):
        return f"Donation from {self.restaurant.restaurant_name} ({self.status})"

# Badge System for Volunteers
class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon_url = models.CharField(max_length=255, blank=True, null=True, help_text="URL or emoji for badge icon")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class VolunteerBadge(models.Model):
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_awarded = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('volunteer', 'badge')

    def __str__(self):
        return f"{self.volunteer.full_name} - {self.badge.name}"
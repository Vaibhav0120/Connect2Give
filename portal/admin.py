from django.contrib import admin
from .models import (
    User, 
    RestaurantProfile, 
    NGOProfile, 
    VolunteerProfile, 
    NGOVolunteer, 
    DonationCamp, 
    Donation
)

# Register your models here.
admin.site.register(User)
admin.site.register(RestaurantProfile)
admin.site.register(NGOProfile)
admin.site.register(VolunteerProfile)
admin.site.register(NGOVolunteer)
admin.site.register(DonationCamp)
admin.site.register(Donation)
from django.contrib import admin
from .models import User, NGOProfile, VolunteerProfile

# Register your models here.
admin.site.register(User)
admin.site.register(NGOProfile)
admin.site.register(VolunteerProfile)
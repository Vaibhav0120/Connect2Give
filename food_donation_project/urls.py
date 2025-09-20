from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add a path for the portal app's URLs
    path('', include('portal.urls')),
]
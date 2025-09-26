from django.contrib import admin
from django.urls import path, include
# --- START: Added Imports ---
from django.conf import settings
from django.conf.urls.static import static
# --- END: Added Imports ---

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
]

# --- START: Added Media URL Pattern ---
# This is crucial for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- END: Added Media URL Pattern ---
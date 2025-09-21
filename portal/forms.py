from django import forms
from .models import DonationCamp, Donation, NGOProfile

class DonationCampForm(forms.ModelForm):
    """
    A form for creating and updating DonationCamp instances.
    """
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Camp Start Time"
    )

    class Meta:
        model = DonationCamp
        fields = ['name', 'location_address', 'start_time', 'latitude', 'longitude']
        labels = {
            'name': 'Camp Name',
            'location_address': 'Camp Location Address',
        }
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class DonationForm(forms.ModelForm):
    """
    A form for Restaurants to create new food Donations.
    """
    class Meta:
        model = Donation
        fields = ['food_description', 'quantity', 'pickup_address']
        labels = {
            'food_description': 'Food Description (e.g., 20 veg thalis, 5kg rice)',
            'quantity': 'Quantity (e.g., number of meals)',
            'pickup_address': 'Pickup Address'
        }
        widgets = {
            'pickup_address': forms.Textarea(attrs={'rows': 3}),
        }

# --- NEW FORM FOR NGO PROFILE ---
class NGOProfileForm(forms.ModelForm):
    """
    A form for NGOs to edit their profile information, including images.
    """
    class Meta:
        model = NGOProfile
        fields = [
            'ngo_name', 
            'address', 
            'contact_person', 
            'latitude', 
            'longitude', 
            'profile_picture', 
            'banner_image'
        ]
        # We don't include registration_number as it shouldn't be editable.
        labels = {
            'ngo_name': 'Organization Name',
            'address': 'Primary Address',
            'contact_person': 'Contact Person Name',
            'profile_picture': 'Profile Picture (Logo)',
            'banner_image': 'Banner Image (for your public page)',
        }
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
from django import forms
from .models import DonationCamp, Donation

class DonationCampForm(forms.ModelForm):
    """
    UPDATED: Now includes hidden fields for coordinates.
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
        # This makes the coordinate fields hidden in the HTML,
        # so they can be controlled by JavaScript.
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
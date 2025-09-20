from django import forms
from .models import DonationCamp

class DonationCampForm(forms.ModelForm):
    """
    A form for creating and updating DonationCamp instances.
    """
    # Using specific input types for a better user experience in the browser
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Camp Start Time"
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Camp End Time"
    )

    class Meta:
        model = DonationCamp
        fields = ['name', 'location_address', 'start_time', 'end_time']
        labels = {
            'name': 'Camp Name',
            'location_address': 'Camp Location Address',
        }
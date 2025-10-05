from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def get_dashboard_url(user):
    """
    Returns the URL for the user's specific dashboard.
    """
    if user.user_type == 'RESTAURANT':
        return reverse('restaurant_dashboard')
    elif user.user_type == 'NGO':
        return reverse('ngo_dashboard_overview')
    elif user.user_type == 'VOLUNTEER':
        return reverse('volunteer_dashboard')
    # For new users, send them to complete their profile
    return reverse('register_step_2')
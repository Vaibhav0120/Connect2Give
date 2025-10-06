# portal/decorators.py
"""
Custom decorators for role-based access control in the Connect2Give application.
"""
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages


def user_type_required(*allowed_user_types):
    """
    Decorator to restrict view access based on user type.
    
    Usage:
        @user_type_required('NGO')
        def ngo_dashboard(request):
            ...
        
        @user_type_required('VOLUNTEER', 'NGO')  # Multiple types allowed
        def shared_view(request):
            ...
    
    Args:
        *allowed_user_types: Variable length argument list of allowed user types.
                            Valid values: 'ADMIN', 'RESTAURANT', 'NGO', 'VOLUNTEER'
    
    Raises:
        PermissionDenied: If user's type is not in the allowed list.
    
    Returns:
        The decorated view function if user type matches, otherwise redirects to index.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('login_page')
            
            # Check if user type is allowed
            if request.user.user_type not in allowed_user_types:
                messages.error(
                    request, 
                    f'Access denied. This page is only accessible to {", ".join(allowed_user_types)} users.'
                )
                return redirect('index')
            
            # User type is allowed, proceed with the view
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(role):
    """
    Decorator to restrict view access based on user role.
    Redirects unauthenticated users to login page.
    Redirects authenticated users with wrong role back to their dashboard.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('login')

            if request.user.role != role:
                messages.error(
                    request,
                    f'Access denied. This page is for {role} users only.'
                )
                if request.user.role == 'company':
                    return redirect('company_upload')
                elif request.user.role == 'annotator':
                    return redirect('annotator_dashboard')
                else:
                    return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

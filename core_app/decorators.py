from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
            super_user_roles = {'BUYER', 'SELLER', 'DRIVER', 'QA'}
            is_super_user_access = user_role == 'SUPER_USER' and bool(super_user_roles.intersection(set(roles)))
            if user_role not in roles and user_role != 'ADMIN_STAFF' and not is_super_user_access:
                messages.error(request, 'You do not have access to that page.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

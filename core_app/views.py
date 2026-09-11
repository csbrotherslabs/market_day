from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Market, Product
from .utils.uploads import reverse_geocode_coordinates, validate_image_upload


def _get_user_city(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.current_city:
        return request.user.profile.current_city
    return request.session.get('current_city', '')


def home(request):
    selected_city = _get_user_city(request)
    markets = Market.objects.filter(active=True)
    no_city_match = False
    if selected_city:
        city_markets = markets.filter(city__iexact=selected_city)
        if city_markets.exists():
            markets = city_markets
        else:
            no_city_match = True
    products = Product.objects.filter(active=True).select_related('seller', 'category')[:8]
    return render(request, 'core_app/home.html', {'markets': markets, 'products': products, 'no_city_match': no_city_match})


def login_view(request):
    if request.method == 'POST':
        login_value = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=login_value, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}.')
            role = getattr(user.profile, 'role', '') if hasattr(user, 'profile') else ''
            if role == 'BUYER':
                return redirect('buyer_dashboard')
            if role == 'SELLER':
                return redirect('seller_dashboard')
            if role == 'DRIVER':
                return redirect('driver_dashboard')
            if role == 'QA':
                return redirect('qa_dashboard')
            if role == 'ADMIN_STAFF' or user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        messages.error(request, 'Invalid username/email or password.')
    return render(request, 'core_app/login.html')


def register_view(request):
    markets = Market.objects.filter(active=True)
    errors = {}
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'BUYER')
        phone = request.POST.get('phone', '').strip()

        if not first_name:
            errors['first_name'] = 'First name is required.'
        if not username:
            errors['username'] = 'Username is required.'
        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
        if not email:
            errors['email'] = 'Email is required.'
        elif User.objects.filter(email__iexact=email).exists():
            errors['email'] = 'An account with this email already exists.'
        if password != confirm_password:
            errors['password'] = 'Passwords do not match.'
        if len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters.'

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.profile.role = role
            user.profile.phone = phone
            user.profile.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('home')
    return render(request, 'core_app/register.html', {'markets': markets, 'errors': errors})


def temporary_password_reset(request):
    # Development-only shortcut. Production must use an authenticated reset method
    # such as Django's signed email token flow.
    if not settings.DEBUG:
        raise Http404

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not email:
            messages.error(request, 'Email is required.')
        elif len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                messages.error(request, 'No account was found with that email address.')
            else:
                user.set_password(new_password)
                user.save(update_fields=['password'])
                messages.success(request, 'Password reset successfully. You can now sign in.')
                return redirect('login')

    return render(request, 'core_app/password_reset_form.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip(); request.user.last_name = request.POST.get('last_name', '').strip(); request.user.email = request.POST.get('email', '').strip().lower(); request.user.save()
        profile.phone = request.POST.get('phone', '').strip(); profile.theme_preference = request.POST.get('theme_preference', profile.theme_preference)
        image = request.FILES.get('profile_image')
        err = validate_image_upload(image)
        if err:
            messages.error(request, err)
            return redirect('profile')
        if image: profile.profile_image = image
        profile.save(); messages.success(request, 'Profile updated successfully.'); return redirect('profile')
    return render(request, 'core_app/profile.html', {'profile': profile})


def market_detail(request, market_id):
    market = get_object_or_404(Market, id=market_id, active=True)
    products = Product.objects.filter(seller__market=market, active=True).select_related('seller', 'category')
    return render(request, 'core_app/market_detail.html', {'market': market, 'products': products})


@require_POST
def location_update(request):
    geo = reverse_geocode_coordinates(request.POST.get('latitude'), request.POST.get('longitude'))
    if request.user.is_authenticated:
        p = request.user.profile
        p.current_city = geo['city']; p.current_region = geo['region']; p.current_country = geo['country']; p.current_latitude = geo['latitude']; p.current_longitude = geo['longitude']; p.save()
    else:
        request.session.update({'current_city': geo['city'], 'current_region': geo['region'], 'current_country': geo['country'], 'current_latitude': str(geo['latitude']), 'current_longitude': str(geo['longitude'])})
    return JsonResponse(geo)


@require_POST
def manual_location_update(request):
    city = request.POST.get('city', '').strip() or 'Unknown Location'; region = request.POST.get('region', '').strip(); country = request.POST.get('country', '').strip()
    if request.user.is_authenticated:
        p = request.user.profile; p.current_city = city; p.current_region = region; p.current_country = country; p.save()
    else:
        request.session.update({'current_city': city, 'current_region': region, 'current_country': country})
    return JsonResponse({'city': city, 'region': region, 'country': country, 'latitude': None, 'longitude': None})

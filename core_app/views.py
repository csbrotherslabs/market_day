from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, Market, Product


def home(request):
    markets = Market.objects.filter(active=True)
    products = Product.objects.filter(active=True).select_related('seller', 'category')[:8]
    stats = {
        'markets': markets.count(),
        'products': Product.objects.filter(active=True).count(),
        'sellers': Product.objects.values('seller').distinct().count(),
        'avg_delivery': '38m',
    }
    return render(request, 'core_app/home.html', {
        'markets': markets,
        'products': products,
        'stats': stats,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}.')
            return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'core_app/login.html')


def register_view(request):
    markets = Market.objects.filter(active=True)
    errors = {}
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
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


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        profile.phone = request.POST.get('phone', '').strip()
        profile.theme_preference = request.POST.get('theme_preference', profile.theme_preference)
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'core_app/profile.html', {'profile': profile})


def market_detail(request, market_id):
    market = get_object_or_404(Market, id=market_id, active=True)
    products = Product.objects.filter(seller__market=market, active=True).select_related('seller', 'category')
    return render(request, 'core_app/market_detail.html', {'market': market, 'products': products})

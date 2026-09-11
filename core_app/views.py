from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import (
    DeliveryAssignment,
    Dispute,
    DriverProfile,
    Market,
    Order,
    OrderItem,
    Product,
    QAProfile,
    QAReport,
    SellerProfile,
    SellerStore,
)
from .utils.uploads import reverse_geocode_coordinates, validate_image_upload


def _get_user_city(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.current_city:
        return request.user.profile.current_city
    return request.session.get('current_city', '')


def _redirect_authenticated_user(user):
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

    products = Product.objects.filter(active=True).select_related('seller', 'store', 'category')[:8]
    context = {
        'markets': markets[:6],
        'products': products,
        'no_city_match': no_city_match,
    }

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        role = request.user.profile.role
        context['home_role'] = role
        context['welcome_name'] = request.user.first_name or request.user.username
        today = timezone.localdate()

        if role == 'SELLER':
            seller_profile, _ = SellerProfile.objects.get_or_create(user=request.user)
            seller_orders = Order.objects.filter(items__seller=seller_profile).distinct().order_by('-created_at')
            seller_items_today = OrderItem.objects.filter(
                seller=seller_profile,
                order__created_at__date=today,
            ).exclude(order__status__in=['CANCELLED', 'QA_REJECTED'])
            context.update({
                'seller_profile': seller_profile,
                'seller_stores': SellerStore.objects.filter(seller=seller_profile).select_related('market').order_by('name')[:4],
                'seller_store_count': SellerStore.objects.filter(seller=seller_profile).count(),
                'seller_product_count': Product.objects.filter(seller=seller_profile, active=True).count(),
                'seller_new_orders': seller_orders.filter(status='CREATED').count(),
                'seller_qa_pending': seller_orders.filter(status__in=['SELLER_CONFIRMED', 'QA_PENDING']).count(),
                'seller_low_stock_count': Product.objects.filter(seller=seller_profile, active=True, available_qty__lte=5).count(),
                'seller_low_stock_products': Product.objects.filter(seller=seller_profile, active=True, available_qty__lte=5).select_related('store').order_by('available_qty')[:5],
                'seller_sales_today': seller_items_today.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00'),
                'seller_recent_orders': seller_orders[:5],
            })

        elif role == 'BUYER':
            buyer_orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
            cart = request.session.get('cart', {})
            context.update({
                'buyer_active_orders': buyer_orders.exclude(status__in=['DELIVERED', 'CANCELLED']).count(),
                'buyer_delivered_orders': buyer_orders.filter(status='DELIVERED').count(),
                'buyer_cart_count': sum(cart.values()) if cart else 0,
                'buyer_recent_orders': buyer_orders[:5],
                'buyer_markets': markets[:4],
                'buyer_products': Product.objects.filter(active=True, store__active=True).select_related('seller', 'store', 'category')[:6],
            })

        elif role == 'DRIVER':
            driver_profile, _ = DriverProfile.objects.get_or_create(user=request.user)
            assignments = DeliveryAssignment.objects.filter(driver=request.user).select_related('order', 'order__market').order_by('-created_at')
            context.update({
                'driver_profile': driver_profile,
                'driver_assigned_count': assignments.filter(status='ASSIGNED').count(),
                'driver_active_count': assignments.filter(status__in=['ASSIGNED', 'ACCEPTED']).count(),
                'driver_completed_today': assignments.filter(status='COMPLETED', delivered_at__date=today).count(),
                'driver_assignments': assignments.exclude(status__in=['COMPLETED', 'DECLINED'])[:6],
                'driver_recent_completed': assignments.filter(status='COMPLETED')[:4],
            })

        elif role == 'QA':
            qa_profile, _ = QAProfile.objects.get_or_create(user=request.user)
            qa_queue = Order.objects.filter(status__in=['SELLER_CONFIRMED', 'QA_PENDING']).select_related('market').order_by('created_at')
            context.update({
                'qa_profile': qa_profile,
                'qa_queue_count': qa_queue.count(),
                'qa_queue': qa_queue[:6],
                'qa_reviewed_today': QAReport.objects.filter(qa_user=request.user, created_at__date=today).count(),
                'qa_approved_today': QAReport.objects.filter(qa_user=request.user, created_at__date=today, result='APPROVED').count(),
                'qa_flagged_today': QAReport.objects.filter(qa_user=request.user, created_at__date=today, result__in=['PARTIAL', 'REJECTED']).count(),
            })

        elif role == 'ADMIN_STAFF':
            context.update({
                'admin_orders_count': Order.objects.count(),
                'admin_open_disputes': Dispute.objects.filter(status__in=['OPEN', 'IN_REVIEW']).count(),
                'admin_pending_delivery': Order.objects.filter(status='DRIVER_PENDING_ASSIGNMENT').count(),
                'admin_users_count': User.objects.count(),
                'admin_recent_orders': Order.objects.select_related('buyer', 'market').order_by('-created_at')[:6],
                'admin_attention_orders': Order.objects.filter(status__in=['DISPUTED', 'QA_REJECTED', 'DRIVER_PENDING_ASSIGNMENT']).select_related('buyer', 'market').order_by('-updated_at')[:6],
            })

        elif role == 'SUPER_USER':
            context.update({
                'super_orders_count': Order.objects.count(),
                'super_markets_count': Market.objects.filter(active=True).count(),
                'super_products_count': Product.objects.filter(active=True).count(),
                'super_open_disputes': Dispute.objects.filter(status__in=['OPEN', 'IN_REVIEW']).count(),
            })

    return render(request, 'core_app/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_authenticated_user(request.user)

    if request.method == 'POST':
        login_value = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=login_value, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}.')
            return _redirect_authenticated_user(user)
        messages.error(request, 'Invalid username/email or password.')
    return render(request, 'core_app/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return _redirect_authenticated_user(request.user)

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
            return _redirect_authenticated_user(user)
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

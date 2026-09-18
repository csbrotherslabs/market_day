from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
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
    # The marketplace is the common landing page for every authenticated role.
    # Role-specific workspaces remain available from account/navigation menus.
    return redirect('home')


def home(request):
    selected_city = _get_user_city(request)
    all_markets = Market.objects.filter(active=True)
    markets = all_markets
    no_city_match = False
    if selected_city:
        city_markets = all_markets.filter(city__iexact=selected_city)
        if city_markets.exists():
            markets = city_markets
        else:
            no_city_match = True

    products = Product.objects.filter(
        active=True,
        available_qty__gt=0,
        store__active=True,
    ).select_related('seller', 'seller__user', 'store', 'store__market', 'category').order_by('-created_at')

    local_products = products
    if selected_city:
        city_products = products.filter(store__market__city__iexact=selected_city)
        if city_products.exists():
            local_products = city_products

    categories = []
    seen_categories = set()
    for product in local_products:
        if product.category and product.category_id not in seen_categories:
            categories.append(product.category)
            seen_categories.add(product.category_id)
        if len(categories) == 10:
            break

    featured_stores = SellerStore.objects.filter(active=True).select_related(
        'seller', 'seller__user', 'market'
    ).order_by('-created_at')
    if selected_city and markets.exists():
        featured_stores = featured_stores.filter(market__in=markets)

    featured_products = local_products.filter(featured=True)[:8]
    discounted_products = local_products.filter(discount_price__isnull=False)[:8]
    promoted_products = local_products.filter(promoted=True)[:8]
    wholesale_products = local_products.filter(is_wholesale=True)[:8]
    made_in_ghana_products = local_products.filter(made_in_ghana=True)[:8]
    new_products = local_products[:8]

    # Until enough order history exists for a ranking model, availability and recency
    # provide a deterministic local fallback for this discovery rail.
    popular_products = local_products.order_by('-available_qty', '-created_at')[:8]

    cart = request.session.get('cart', {})
    context = {
        'markets': markets[:8],
        'categories': categories,
        'featured_products': featured_products,
        'discounted_products': discounted_products,
        'fresh_products': local_products[:8],
        'popular_products': popular_products,
        'promoted_products': promoted_products,
        'featured_stores': featured_stores[:6],
        'wholesale_products': wholesale_products,
        'made_in_ghana_products': made_in_ghana_products,
        'new_products': new_products,
        'no_city_match': no_city_match,
        'selected_city': selected_city,
        'cart_count': sum(cart.values()) if cart else 0,
    }
    return render(request, 'core_app/home.html', context)


MARKETPLACE_COLLECTIONS = {
    'featured': ('Featured Products', 'Products selected for extra visibility on Market Day.'),
    'deals': ("Today's Deals", 'Current products with seller discounts.'),
    'fresh': ('Fresh From the Market', 'Recently listed products currently in stock.'),
    'popular': ('Popular Near You', 'Well-stocked local products worth discovering.'),
    'promoted': ('Promoted Products', 'Sponsored placements from Market Day sellers.'),
    'wholesale': ('Wholesale & Bulk Deals', 'Larger quantities for traders, restaurants and businesses.'),
    'made-in-ghana': ('Made in Ghana', 'Products from Ghanaian producers and businesses.'),
    'new': ('New on Market Day', 'Recently added marketplace products.'),
}


def _marketplace_products(request):
    products = Product.objects.filter(
        active=True, available_qty__gt=0, store__active=True
    ).select_related('seller', 'seller__user', 'store', 'store__market', 'category')
    city = _get_user_city(request)
    if city:
        local = products.filter(store__market__city__iexact=city)
        if local.exists():
            products = local
    return products


def _apply_product_filters(request, products):
    query = request.GET.get('q', '').strip()
    market_id = request.GET.get('market', '').strip()
    sort = request.GET.get('sort', 'recommended')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) |
            Q(store__name__icontains=query) | Q(store__market__name__icontains=query)
        )
    if market_id.isdigit():
        products = products.filter(store__market_id=int(market_id))
    if request.GET.get('deals') == '1':
        products = products.filter(discount_price__isnull=False)
    if request.GET.get('ghana') == '1':
        products = products.filter(made_in_ghana=True)
    if request.GET.get('wholesale') == '1':
        products = products.filter(is_wholesale=True)
    if sort == 'price-low':
        products = products.order_by('price', '-created_at')
    elif sort == 'price-high':
        products = products.order_by('-price', '-created_at')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-featured', '-promoted', '-available_qty', '-created_at')
    return products, query, sort


def public_storefront(request, store_id):
    store = get_object_or_404(
        SellerStore.objects.select_related('seller', 'seller__user', 'market'),
        id=store_id,
        active=True,
        seller__active=True,
    )
    products = Product.objects.filter(
        store=store, active=True, available_qty__gt=0
    ).select_related('seller', 'seller__user', 'store', 'store__market', 'category').order_by('-created_at')
    products, query, sort = _apply_product_filters(request, products)
    return render(request, 'core_app/public_storefront.html', {
        'store': store,
        'seller': store.seller,
        'products': products,
        'query': query,
        'sort': sort,
    })


def product_collection(request, collection):
    if collection not in MARKETPLACE_COLLECTIONS:
        raise Http404
    products = _marketplace_products(request)
    if collection == 'featured':
        products = products.filter(featured=True)
    elif collection == 'deals':
        products = products.filter(discount_price__isnull=False)
    elif collection == 'promoted':
        products = products.filter(promoted=True)
    elif collection == 'wholesale':
        products = products.filter(is_wholesale=True)
    elif collection == 'made-in-ghana':
        products = products.filter(made_in_ghana=True)
    elif collection == 'popular':
        products = products.order_by('-available_qty', '-created_at')
    else:
        products = products.order_by('-created_at')
    products, query, sort = _apply_product_filters(request, products)
    title, subtitle = MARKETPLACE_COLLECTIONS[collection]
    return render(request, 'core_app/product_listing.html', {
        'page_title': title,
        'page_subtitle': subtitle,
        'products': products,
        'markets': Market.objects.filter(active=True).order_by('name'),
        'query': query,
        'sort': sort,
        'collection': collection,
        'is_sponsored_collection': collection == 'promoted',
    })


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id, active=True)
    products = _marketplace_products(request).filter(category=category)
    products, query, sort = _apply_product_filters(request, products)
    return render(request, 'core_app/product_listing.html', {
        'page_title': category.name,
        'page_subtitle': 'Browse available products in this category.',
        'products': products,
        'markets': Market.objects.filter(active=True).order_by('name'),
        'query': query,
        'sort': sort,
        'category': category,
    })


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
        profile.save(); messages.success(request, 'Account information updated successfully.'); return redirect('/accounts/profile/?view=settings')
    return render(request, 'core_app/profile.html', {
        'profile': profile,
        'settings_view': request.GET.get('view') == 'settings',
    })


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

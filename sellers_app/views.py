from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import Category, Market, Order, Product, SellerProfile, SellerStore


STORE_TEMPLATES = {
    'fresh_simple': {
        'name': 'Fresh & Simple',
        'badge': 'Most Popular',
        'complexity': 'Simple',
        'description': 'A clean, modern storefront focused on freshness and easy shopping.',
        'features': ['Hero banner + logo', 'Product grid', 'Category menu', 'Store information'],
        'required_fields': ['tagline'],
    },
    'boutique': {
        'name': 'Boutique',
        'badge': 'Brand Focused',
        'complexity': 'Moderate',
        'description': 'A polished storefront for specialty foods, spices, herbs, and distinctive brands.',
        'features': ['Hero banner + logo', 'Featured categories', 'About section', 'Contact information'],
        'required_fields': ['tagline', 'about_story', 'contact_phone'],
    },
    'story_impact': {
        'name': 'Story & Impact',
        'badge': 'Community',
        'complexity': 'Moderate',
        'description': 'Tell your story, mission, and community impact while showcasing your products.',
        'features': ['Hero banner + logo', 'Our story section', 'Product categories', 'Impact information'],
        'required_fields': ['tagline', 'about_story', 'impact_statement', 'contact_phone'],
    },
    'modern_market': {
        'name': 'Modern Market',
        'badge': 'Feature Rich',
        'complexity': 'Advanced',
        'description': 'A versatile storefront with promotions, featured products, and stronger merchandising.',
        'features': ['Hero banner + logo', 'Promotions section', 'Category showcase', 'Featured products'],
        'required_fields': ['tagline', 'promotion_text', 'featured_category', 'contact_phone'],
    },
    'premium_showcase': {
        'name': 'Premium Showcase',
        'badge': 'Premium',
        'complexity': 'Advanced',
        'description': 'A premium presentation for established sellers who want deeper brand storytelling.',
        'features': ['Hero banner + logo', 'Featured collections', 'Customer trust section', 'Brand story'],
        'required_fields': ['tagline', 'about_story', 'featured_collection', 'quality_promise', 'contact_phone'],
    },
    'creative_unique': {
        'name': 'Creative & Unique',
        'badge': 'Most Customizable',
        'complexity': 'Expert',
        'description': 'A visually rich storefront with flexible storytelling and custom merchandising areas.',
        'features': ['Hero banner + logo', 'Gallery / highlights', 'Custom headline', 'About / story section'],
        'required_fields': ['tagline', 'custom_headline', 'about_story', 'gallery_intro', 'contact_phone', 'social_handle'],
    },
}

STORE_FIELD_LABELS = {
    'tagline': 'Store tagline',
    'about_story': 'About your store / brand story',
    'impact_statement': 'Community impact statement',
    'promotion_text': 'Promotion message',
    'featured_category': 'Featured category',
    'featured_collection': 'Featured collection title',
    'quality_promise': 'Quality promise',
    'custom_headline': 'Custom hero headline',
    'gallery_intro': 'Gallery / highlights introduction',
    'contact_phone': 'Customer contact phone',
    'social_handle': 'Social media handle',
}


def _get_seller_profile(user):
    profile, created = SellerProfile.objects.get_or_create(user=user)
    return profile


def _store_form_context(store=None, selected_template='', markets=None, errors=None, form_values=None):
    template = STORE_TEMPLATES.get(selected_template)
    return {
        'store': store,
        'markets': markets or Market.objects.filter(active=True),
        'store_templates': STORE_TEMPLATES,
        'selected_template_key': selected_template,
        'selected_template': template,
        'errors': errors or {},
        'form_values': form_values or {},
        'field_labels': STORE_FIELD_LABELS,
    }


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def dashboard(request):
    seller_profile = _get_seller_profile(request.user)
    stores = SellerStore.objects.filter(seller=seller_profile).select_related('market').order_by('name')
    products = Product.objects.filter(seller=seller_profile).select_related('store')[:6]
    orders = Order.objects.filter(items__seller=seller_profile).distinct()[:8]
    return render(request, 'sellers_app/dashboard.html', {
        'seller_profile': seller_profile,
        'stores': stores,
        'products': products,
        'orders': orders,
    })


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def store_setup(request, store_id=None):
    seller_profile = _get_seller_profile(request.user)
    store = None
    if store_id is not None:
        store = get_object_or_404(SellerStore, id=store_id, seller=seller_profile)

    markets = Market.objects.filter(active=True).order_by('name')
    selected_template = (
        request.POST.get('template_key', '').strip()
        if request.method == 'POST'
        else request.GET.get('template', '').strip()
    )
    if store and not selected_template:
        selected_template = store.template_key or 'fresh_simple'

    # New stores begin on the template-selection screen.
    if store is None and request.method == 'GET' and selected_template not in STORE_TEMPLATES:
        return render(request, 'sellers_app/store_setup.html', _store_form_context(
            store=store,
            selected_template='',
            markets=markets,
        ))

    if selected_template not in STORE_TEMPLATES:
        messages.error(request, 'Select a valid store design.')
        return render(request, 'sellers_app/store_setup.html', _store_form_context(
            store=store,
            selected_template='',
            markets=markets,
        ))

    template_config = STORE_TEMPLATES[selected_template]

    if request.method == 'POST':
        form_values = {
            'name': request.POST.get('name', '').strip(),
            'market': request.POST.get('market', '').strip(),
            'stall_number': request.POST.get('stall_number', '').strip(),
            'description': request.POST.get('description', '').strip(),
        }
        for field in STORE_FIELD_LABELS:
            form_values[field] = request.POST.get(field, '').strip()

        errors = {}
        if not form_values['name']:
            errors['name'] = 'Store name is required.'
        if not form_values['market']:
            errors['market'] = 'Market is required.'
        elif not markets.filter(id=form_values['market']).exists():
            errors['market'] = 'Select a valid active market.'
        if not form_values['description']:
            errors['description'] = 'Store description is required.'

        for field in template_config['required_fields']:
            if not form_values.get(field):
                errors[field] = f'{STORE_FIELD_LABELS[field]} is required for this design.'

        if store is None and not request.FILES.get('store_image'):
            errors['store_image'] = 'A hero/banner image is required.'
        if store is None and not request.FILES.get('logo_image'):
            errors['logo_image'] = 'A store logo is required.'

        if errors:
            messages.error(request, 'Complete all required fields before creating your store.')
            return render(request, 'sellers_app/store_setup.html', _store_form_context(
                store=store,
                selected_template=selected_template,
                markets=markets,
                errors=errors,
                form_values=form_values,
            ))

        if store is None:
            store = SellerStore(seller=seller_profile)

        store.market_id = form_values['market']
        store.name = form_values['name']
        store.stall_number = form_values['stall_number']
        store.description = form_values['description']
        store.template_key = selected_template
        store.template_data = {
            field: form_values.get(field, '')
            for field in STORE_FIELD_LABELS
            if form_values.get(field, '')
        }
        store.active = request.POST.get('active') == 'on' if store.pk else True
        if request.FILES.get('store_image'):
            store.store_image = request.FILES['store_image']
        if request.FILES.get('logo_image'):
            store.logo_image = request.FILES['logo_image']
        store.save()

        messages.success(request, f'{store.name} was saved with the {template_config["name"]} design.')
        return redirect('seller_dashboard')

    form_values = {}
    if store:
        form_values = {
            'name': store.name,
            'market': str(store.market_id or ''),
            'stall_number': store.stall_number,
            'description': store.description,
            **(store.template_data or {}),
        }

    return render(request, 'sellers_app/store_setup.html', _store_form_context(
        store=store,
        selected_template=selected_template,
        markets=markets,
        form_values=form_values,
    ))


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def product_list(request):
    seller_profile = _get_seller_profile(request.user)
    products = Product.objects.filter(seller=seller_profile).select_related('store', 'category')
    return render(request, 'sellers_app/products.html', {'products': products})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def add_product(request):
    seller_profile = _get_seller_profile(request.user)
    categories = Category.objects.filter(active=True)
    stores = SellerStore.objects.filter(seller=seller_profile, active=True).select_related('market').order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        unit = request.POST.get('unit', 'piece').strip()
        available_qty = request.POST.get('available_qty', '0').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category') or None
        store_id = request.POST.get('store') or None

        store = SellerStore.objects.filter(id=store_id, seller=seller_profile, active=True).first() if store_id else None
        if not stores.exists():
            messages.error(request, 'Create a store before adding products.')
        elif not store:
            messages.error(request, 'Select one of your stores.')
        elif not name or not price:
            messages.error(request, 'Name and price are required.')
        else:
            try:
                parsed_price = Decimal(price)
                parsed_qty = int(available_qty or 0)
                if parsed_price < 0 or parsed_qty < 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                messages.error(request, 'Enter a valid non-negative price and quantity.')
            else:
                product = Product(
                    seller=seller_profile,
                    store=store,
                    category_id=category_id,
                    name=name,
                    description=description,
                    price=parsed_price,
                    unit=unit,
                    available_qty=parsed_qty,
                    active=True,
                )
                if request.FILES.get('image'):
                    product.image = request.FILES['image']
                product.save()
                messages.success(request, f'Product added to {store.name}.')
                return redirect('seller_products')

    return render(request, 'sellers_app/add_product.html', {'categories': categories, 'stores': stores})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def edit_product(request, product_id):
    seller_profile = _get_seller_profile(request.user)
    product = get_object_or_404(Product, id=product_id, seller=seller_profile)
    categories = Category.objects.filter(active=True)
    stores = SellerStore.objects.filter(seller=seller_profile, active=True).select_related('market').order_by('name')

    if request.method == 'POST':
        store_id = request.POST.get('store') or None
        store = SellerStore.objects.filter(id=store_id, seller=seller_profile, active=True).first() if store_id else None
        if not store:
            messages.error(request, 'Select one of your stores.')
        else:
            try:
                parsed_price = Decimal(request.POST.get('price', product.price))
                parsed_qty = int(request.POST.get('available_qty', product.available_qty) or 0)
                if parsed_price < 0 or parsed_qty < 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                messages.error(request, 'Enter a valid non-negative price and quantity.')
            else:
                product.store = store
                product.name = request.POST.get('name', product.name).strip()
                product.price = parsed_price
                product.unit = request.POST.get('unit', product.unit).strip()
                product.available_qty = parsed_qty
                product.description = request.POST.get('description', product.description).strip()
                product.category_id = request.POST.get('category') or None
                product.active = request.POST.get('active') == 'on'
                if request.FILES.get('image'):
                    product.image = request.FILES['image']
                product.save()
                messages.success(request, 'Product updated successfully.')
                return redirect('seller_products')

    return render(request, 'sellers_app/edit_product.html', {
        'product': product,
        'categories': categories,
        'stores': stores,
    })


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def order_list(request):
    seller_profile = _get_seller_profile(request.user)
    orders = Order.objects.filter(items__seller=seller_profile).distinct()
    return render(request, 'sellers_app/orders.html', {'orders': orders})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def order_detail(request, order_id):
    seller_profile = _get_seller_profile(request.user)
    order = get_object_or_404(Order.objects.filter(items__seller=seller_profile).distinct(), id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            order.status = 'SELLER_CONFIRMED'
            order.save(update_fields=['status'])
            messages.success(request, 'Order confirmed and moved to seller confirmed.')
        elif action == 'qa_pending':
            order.status = 'QA_PENDING'
            order.save(update_fields=['status'])
            messages.success(request, 'Order sent to QA queue.')
        elif action == 'cancel':
            order.status = 'CANCELLED'
            order.save(update_fields=['status'])
            messages.success(request, 'Order cancelled.')
        return redirect('seller_order_detail', order_id=order.id)
    return render(request, 'sellers_app/order_detail.html', {'order': order})

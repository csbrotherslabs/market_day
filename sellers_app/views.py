from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import Category, Market, Order, Product, SellerProfile, SellerStore


def _get_seller_profile(user):
    profile, created = SellerProfile.objects.get_or_create(user=user)
    return profile


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
    markets = Market.objects.filter(active=True)

    if request.method == 'POST':
        market_id = request.POST.get('market') or None
        name = request.POST.get('name', '').strip()
        stall_number = request.POST.get('stall_number', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'Store name is required.')
        else:
            if store is None:
                store = SellerStore(seller=seller_profile)
            store.market_id = market_id
            store.name = name
            store.stall_number = stall_number
            store.description = description
            store.active = request.POST.get('active') == 'on' if store.pk else True
            if request.FILES.get('store_image'):
                store.store_image = request.FILES['store_image']
            store.save()
            messages.success(request, 'Store saved successfully.')
            return redirect('seller_dashboard')

    return render(request, 'sellers_app/store_setup.html', {
        'seller_profile': seller_profile,
        'store': store,
        'markets': markets,
    })


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

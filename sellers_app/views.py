from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import Category, Market, Order, Product, SellerProfile


def _get_seller_profile(user):
    profile, created = SellerProfile.objects.get_or_create(user=user)
    return profile


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def dashboard(request):
    seller_profile = _get_seller_profile(request.user)
    products = Product.objects.filter(seller=seller_profile)[:6]
    orders = Order.objects.filter(items__seller=seller_profile).distinct()[:8]
    return render(request, 'sellers_app/dashboard.html', {'seller_profile': seller_profile, 'products': products, 'orders': orders})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def store_setup(request):
    seller_profile = _get_seller_profile(request.user)
    markets = Market.objects.filter(active=True)
    if request.method == 'POST':
        seller_profile.market_id = request.POST.get('market') or None
        seller_profile.stall_name = request.POST.get('stall_name', '').strip()
        seller_profile.stall_number = request.POST.get('stall_number', '').strip()
        seller_profile.description = request.POST.get('description', '').strip()
        seller_profile.save()
        messages.success(request, 'Store profile updated successfully.')
        return redirect('seller_dashboard')
    return render(request, 'sellers_app/store_setup.html', {'seller_profile': seller_profile, 'markets': markets})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def product_list(request):
    seller_profile = _get_seller_profile(request.user)
    products = Product.objects.filter(seller=seller_profile)
    return render(request, 'sellers_app/products.html', {'products': products})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def add_product(request):
    seller_profile = _get_seller_profile(request.user)
    categories = Category.objects.filter(active=True)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        unit = request.POST.get('unit', 'piece').strip()
        available_qty = request.POST.get('available_qty', '0').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category') or None
        if not name or not price:
            messages.error(request, 'Name and price are required.')
        else:
            product = Product(
                seller=seller_profile,
                category_id=category_id,
                name=name,
                description=description,
                price=Decimal(price),
                unit=unit,
                available_qty=int(available_qty or 0),
                active=True,
            )
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            product.save()
            messages.success(request, 'Product created successfully.')
            return redirect('seller_products')
    return render(request, 'sellers_app/add_product.html', {'categories': categories})


@login_required
@role_required(['SELLER', 'SUPER_USER', 'ADMIN_STAFF'])
def edit_product(request, product_id):
    seller_profile = _get_seller_profile(request.user)
    product = get_object_or_404(Product, id=product_id, seller=seller_profile)
    categories = Category.objects.filter(active=True)
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name).strip()
        product.price = Decimal(request.POST.get('price', product.price))
        product.unit = request.POST.get('unit', product.unit).strip()
        product.available_qty = int(request.POST.get('available_qty', product.available_qty) or 0)
        product.description = request.POST.get('description', product.description).strip()
        product.category_id = request.POST.get('category') or None
        product.active = request.POST.get('active') == 'on'
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('seller_products')
    return render(request, 'sellers_app/edit_product.html', {'product': product, 'categories': categories})


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

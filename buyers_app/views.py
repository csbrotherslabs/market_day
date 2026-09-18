from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import Dispute, Market, Order, OrderItem, Product, Rating

SHOPPER_ROLES = ['BUYER', 'SELLER', 'DRIVER', 'QA', 'SUPER_USER', 'ADMIN_STAFF']


def _get_cart(session):
    return session.setdefault('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


@login_required
@role_required(SHOPPER_ROLES)
def dashboard(request):
    orders = Order.objects.filter(buyer=request.user)[:6]
    markets = Market.objects.filter(active=True)[:6]
    return render(request, 'buyers_app/dashboard.html', {'orders': orders, 'markets': markets})


@login_required
@role_required(SHOPPER_ROLES)
def market_products(request, market_id):
    market = get_object_or_404(Market, id=market_id, active=True)
    base_products = Product.objects.filter(
        store__market=market,
        store__active=True,
        seller__active=True,
        active=True,
        available_qty__gt=0,
    ).select_related('seller', 'seller__user', 'store', 'store__market', 'category')

    categories = (
        base_products.filter(category__isnull=False)
        .values('category_id', 'category__name')
        .distinct()
        .order_by('category__name')
    )
    stores = (
        base_products.filter(store__isnull=False)
        .values('store_id', 'store__name')
        .distinct()
        .order_by('store__name')
    )

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    store_id = request.GET.get('store', '').strip()
    sort = request.GET.get('sort', 'recommended')
    deals = request.GET.get('deals') == '1'
    ghana = request.GET.get('ghana') == '1'
    wholesale = request.GET.get('wholesale') == '1'

    products = base_products
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(store__name__icontains=query)
            | Q(seller__stall_name__icontains=query)
            | Q(category__name__icontains=query)
        )
    if category_id.isdigit():
        products = products.filter(category_id=int(category_id))
    if store_id.isdigit():
        products = products.filter(store_id=int(store_id))
    if deals:
        products = products.filter(discount_price__isnull=False, discount_price__lt=F('price'))
    if ghana:
        products = products.filter(made_in_ghana=True)
    if wholesale:
        products = products.filter(is_wholesale=True)

    if sort == 'price-low':
        products = products.order_by('price', '-created_at')
    elif sort == 'price-high':
        products = products.order_by('-price', '-created_at')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'rating':
        products = products.order_by('-seller__rating_avg', '-featured', '-created_at')
    else:
        products = products.order_by('-featured', '-promoted', '-seller__rating_avg', '-available_qty', '-created_at')

    return render(request, 'buyers_app/market_products.html', {
        'market': market,
        'products': products,
        'categories': categories,
        'stores': stores,
        'query': query,
        'selected_category': category_id,
        'selected_store': store_id,
        'sort': sort,
        'deals': deals,
        'ghana': ghana,
        'wholesale': wholesale,
        'result_count': products.count(),
    })


@login_required
@role_required(SHOPPER_ROLES)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)
    qty = int(request.POST.get('qty', 1) or 1)
    cart = _get_cart(request.session)
    product_key = str(product.id)
    cart[product_key] = cart.get(product_key, 0) + max(1, qty)
    _save_cart(request.session, cart)
    cart_count = sum(cart.values())
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'product_id': product.id,
            'product_name': product.name,
            'cart_count': cart_count,
            'product_qty': cart[product_key],
        })
    messages.success(request, f'{product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'buyer_cart'))


@login_required
@role_required(SHOPPER_ROLES)
def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    _save_cart(request.session, cart)
    messages.success(request, 'Item removed from cart.')
    return redirect('buyer_cart')


@login_required
@role_required(SHOPPER_ROLES)
def cart_view(request):
    cart = _get_cart(request.session)
    product_ids = [int(pid) for pid in cart.keys()] if cart else []
    products = Product.objects.filter(id__in=product_ids).select_related('seller', 'store')
    items = []
    subtotal = Decimal('0.00')
    for product in products:
        qty = cart.get(str(product.id), 0)
        unit_price = product.discount_price if product.discount_price is not None and product.discount_price < product.price else product.price
        line_total = unit_price * qty
        subtotal += line_total
        items.append({'product': product, 'qty': qty, 'unit_price': unit_price, 'line_total': line_total})
    delivery_fee = Decimal('15.00') if items else Decimal('0.00')
    total = subtotal + delivery_fee
    return render(request, 'buyers_app/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
    })


@login_required
@role_required(SHOPPER_ROLES)
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('buyer_cart')

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids).select_related('seller', 'store__market')
    subtotal = Decimal('0.00')
    for product in products:
        unit_price = product.discount_price if product.discount_price is not None and product.discount_price < product.price else product.price
        subtotal += unit_price * cart[str(product.id)]
    delivery_fee = Decimal('15.00')
    total = subtotal + delivery_fee

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '').strip()
        delivery_landmark = request.POST.get('delivery_landmark', '').strip()
        delivery_phone = request.POST.get('delivery_phone', '').strip()
        if not delivery_address or not delivery_phone:
            messages.error(request, 'Delivery address and phone are required.')
        else:
            first_product = products.first()
            first_market = first_product.store.market if first_product and first_product.store else None
            order = Order.objects.create(
                buyer=request.user,
                market=first_market,
                status='CREATED',
                delivery_address=delivery_address,
                delivery_landmark=delivery_landmark,
                delivery_phone=delivery_phone,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=total,
            )
            for product in products:
                qty = cart[str(product.id)]
                unit_price = product.discount_price if product.discount_price is not None and product.discount_price < product.price else product.price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    seller=product.seller,
                    qty_requested=qty,
                    unit_price=unit_price,
                    line_total=unit_price * qty,
                )
            request.session['cart'] = {}
            request.session.modified = True
            messages.success(request, f'Order #{order.id} placed successfully.')
            return redirect('buyer_order_detail', order_id=order.id)

    return render(request, 'buyers_app/checkout.html', {
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
    })


@login_required
@role_required(SHOPPER_ROLES)
def order_history(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'buyers_app/orders.html', {'orders': orders})


@login_required
@role_required(SHOPPER_ROLES)
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    assignment = getattr(order, 'deliveryassignment', None)
    qa_report = getattr(order, 'qareport', None)
    return render(request, 'buyers_app/order_detail.html', {'order': order, 'assignment': assignment, 'qa_report': qa_report})


@login_required
@role_required(SHOPPER_ROLES)
def create_dispute(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    if request.method == 'POST':
        category = request.POST.get('category', '').strip()
        details = request.POST.get('details', '').strip()
        if not category or not details:
            messages.error(request, 'Category and details are required.')
        else:
            Dispute.objects.create(order=order, opened_by=request.user, category=category, details=details)
            order.status = 'DISPUTED'
            order.save(update_fields=['status'])
            messages.success(request, 'Dispute submitted successfully.')
            return redirect('buyer_order_detail', order_id=order.id)
    return render(request, 'buyers_app/create_dispute.html', {'order': order})


@login_required
@role_required(SHOPPER_ROLES)
def create_rating(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    if request.method == 'POST':
        score = int(request.POST.get('score', 5) or 5)
        comment = request.POST.get('comment', '').strip()
        first_seller = order.items.first().seller if order.items.exists() else None
        driver = order.deliveryassignment.driver if hasattr(order, 'deliveryassignment') else None
        Rating.objects.create(order=order, buyer=request.user, seller=first_seller, driver=driver, score=score, comment=comment)
        messages.success(request, 'Thank you for your rating.')
        return redirect('buyer_order_detail', order_id=order.id)
    return render(request, 'buyers_app/create_rating.html', {'order': order})

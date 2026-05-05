from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import Dispute, Market, Order, OrderItem, Product, Rating


def _get_cart(session):
    return session.setdefault('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


@login_required
@role_required(['BUYER'])
def dashboard(request):
    orders = Order.objects.filter(buyer=request.user)[:6]
    markets = Market.objects.filter(active=True)[:6]
    return render(request, 'buyers_app/dashboard.html', {'orders': orders, 'markets': markets})


@login_required
@role_required(['BUYER'])
def market_products(request, market_id):
    market = get_object_or_404(Market, id=market_id)
    products = Product.objects.filter(seller__market=market, active=True).select_related('seller', 'category')
    return render(request, 'buyers_app/market_products.html', {'market': market, 'products': products})


@login_required
@role_required(['BUYER'])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)
    qty = int(request.POST.get('qty', 1) or 1)
    cart = _get_cart(request.session)
    product_key = str(product.id)
    cart[product_key] = cart.get(product_key, 0) + max(1, qty)
    _save_cart(request.session, cart)
    messages.success(request, f'{product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'buyer_cart'))


@login_required
@role_required(['BUYER'])
def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    _save_cart(request.session, cart)
    messages.success(request, 'Item removed from cart.')
    return redirect('buyer_cart')


@login_required
@role_required(['BUYER'])
def cart_view(request):
    cart = _get_cart(request.session)
    product_ids = [int(pid) for pid in cart.keys()] if cart else []
    products = Product.objects.filter(id__in=product_ids).select_related('seller')
    items = []
    subtotal = Decimal('0.00')
    for product in products:
        qty = cart.get(str(product.id), 0)
        line_total = product.price * qty
        subtotal += line_total
        items.append({'product': product, 'qty': qty, 'line_total': line_total})
    delivery_fee = Decimal('15.00') if items else Decimal('0.00')
    total = subtotal + delivery_fee
    return render(request, 'buyers_app/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
    })


@login_required
@role_required(['BUYER'])
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('buyer_cart')

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids).select_related('seller__market')
    subtotal = Decimal('0.00')
    for product in products:
        subtotal += product.price * cart[str(product.id)]
    delivery_fee = Decimal('15.00')
    total = subtotal + delivery_fee

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '').strip()
        delivery_landmark = request.POST.get('delivery_landmark', '').strip()
        delivery_phone = request.POST.get('delivery_phone', '').strip()
        if not delivery_address or not delivery_phone:
            messages.error(request, 'Delivery address and phone are required.')
        else:
            first_market = products.first().seller.market if products.first() else None
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
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    seller=product.seller,
                    qty_requested=qty,
                    unit_price=product.price,
                    line_total=product.price * qty,
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
@role_required(['BUYER'])
def order_history(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'buyers_app/orders.html', {'orders': orders})


@login_required
@role_required(['BUYER'])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    assignment = getattr(order, 'deliveryassignment', None)
    qa_report = getattr(order, 'qareport', None)
    return render(request, 'buyers_app/order_detail.html', {'order': order, 'assignment': assignment, 'qa_report': qa_report})


@login_required
@role_required(['BUYER'])
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
@role_required(['BUYER'])
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

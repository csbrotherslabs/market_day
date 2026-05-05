from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import AdminActionLog, DeliveryAssignment, Dispute, DriverProfile, Order


@login_required
@role_required(['ADMIN_STAFF'])
def dashboard(request):
    context = {
        'orders_count': Order.objects.count(),
        'disputes_open': Dispute.objects.filter(status__in=['OPEN', 'IN_REVIEW']).count(),
        'drivers_count': DriverProfile.objects.count(),
        'recent_orders': Order.objects.all()[:8],
    }
    return render(request, 'adminops_app/dashboard.html', context)


@login_required
@role_required(['ADMIN_STAFF'])
def order_list(request):
    status = request.GET.get('status', '').strip()
    orders = Order.objects.all()
    if status:
        orders = orders.filter(status=status)
    return render(request, 'adminops_app/orders.html', {'orders': orders, 'status': status})


@login_required
@role_required(['ADMIN_STAFF'])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    drivers = User.objects.filter(profile__role='DRIVER')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign_driver':
            driver_id = request.POST.get('driver_id')
            driver = get_object_or_404(User, id=driver_id, profile__role='DRIVER')
            assignment, created = DeliveryAssignment.objects.update_or_create(
                order=order,
                defaults={'driver': driver, 'assigned_by': request.user, 'status': 'ASSIGNED'}
            )
            order.status = 'DRIVER_ASSIGNED'
            order.save(update_fields=['status'])
            AdminActionLog.objects.create(admin_user=request.user, action_type='Assign Driver', target_type='Order', target_id=order.id, details=f'Driver: {driver.username}')
            messages.success(request, 'Driver assigned successfully.')
        elif action == 'cancel_order':
            order.status = 'CANCELLED'
            order.save(update_fields=['status'])
            AdminActionLog.objects.create(admin_user=request.user, action_type='Cancel Order', target_type='Order', target_id=order.id)
            messages.success(request, 'Order cancelled.')
        elif action == 'mark_disputed':
            order.status = 'DISPUTED'
            order.save(update_fields=['status'])
            AdminActionLog.objects.create(admin_user=request.user, action_type='Mark Disputed', target_type='Order', target_id=order.id)
            messages.success(request, 'Order marked as disputed.')
        return redirect('admin_order_detail', order_id=order.id)
    return render(request, 'adminops_app/order_detail.html', {'order': order, 'drivers': drivers})


@login_required
@role_required(['ADMIN_STAFF'])
def user_list(request):
    users = User.objects.select_related('profile').all()
    return render(request, 'adminops_app/users.html', {'users': users})


@login_required
@role_required(['ADMIN_STAFF'])
def dispute_list(request):
    disputes = Dispute.objects.select_related('order', 'opened_by').all()
    if request.method == 'POST':
        dispute_id = request.POST.get('dispute_id')
        status = request.POST.get('status')
        resolution_notes = request.POST.get('resolution_notes', '').strip()
        dispute = get_object_or_404(Dispute, id=dispute_id)
        dispute.status = status
        dispute.resolution_notes = resolution_notes
        dispute.save()
        AdminActionLog.objects.create(admin_user=request.user, action_type='Resolve Dispute', target_type='Dispute', target_id=dispute.id, details=status)
        messages.success(request, 'Dispute updated successfully.')
        return redirect('admin_disputes')
    return render(request, 'adminops_app/disputes.html', {'disputes': disputes})

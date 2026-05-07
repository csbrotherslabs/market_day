from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from core_app.decorators import role_required
from core_app.models import Order, QAProfile, QAReport


@login_required
@role_required(['QA', 'SUPER_USER', 'ADMIN_STAFF'])
def dashboard(request):
    QAProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(status__in=['QA_PENDING', 'SELLER_CONFIRMED'])
    return render(request, 'qa_app/dashboard.html', {'orders': orders})


@login_required
@role_required(['QA', 'SUPER_USER', 'ADMIN_STAFF'])
def order_review(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    existing_report = QAReport.objects.filter(order=order).first()
    if request.method == 'POST':
        result = request.POST.get('result', '').strip()
        notes = request.POST.get('notes', '').strip()
        if result not in ['APPROVED', 'PARTIAL', 'REJECTED']:
            messages.error(request, 'Select a valid QA result.')
        else:
            report, created = QAReport.objects.update_or_create(
                order=order,
                defaults={'qa_user': request.user, 'result': result, 'notes': notes}
            )
            if result == 'APPROVED':
                order.status = 'DRIVER_PENDING_ASSIGNMENT'
            elif result == 'PARTIAL':
                order.status = 'QA_PARTIAL'
            else:
                order.status = 'QA_REJECTED'
            order.save(update_fields=['status'])
            messages.success(request, 'QA review submitted successfully.')
            return redirect('qa_dashboard')
    return render(request, 'qa_app/order_review.html', {'order': order, 'existing_report': existing_report})

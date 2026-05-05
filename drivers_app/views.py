from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from core_app.decorators import role_required
from core_app.models import DeliveryAssignment, DriverProfile


@login_required
@role_required(['DRIVER'])
def dashboard(request):
    DriverProfile.objects.get_or_create(user=request.user)
    assignments = DeliveryAssignment.objects.filter(driver=request.user)
    return render(request, 'drivers_app/dashboard.html', {'assignments': assignments})


@login_required
@role_required(['DRIVER'])
def profile_setup(request):
    profile, created = DriverProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.vehicle_type = request.POST.get('vehicle_type', '').strip()
        profile.license_id = request.POST.get('license_id', '').strip()
        profile.region = request.POST.get('region', '').strip()
        profile.save()
        messages.success(request, 'Driver profile updated successfully.')
        return redirect('driver_dashboard')
    return render(request, 'drivers_app/profile_setup.html', {'profile': profile})


@login_required
@role_required(['DRIVER'])
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(DeliveryAssignment, id=assignment_id, driver=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            assignment.status = 'ACCEPTED'
            assignment.order.status = 'DRIVER_ASSIGNED'
            assignment.order.save(update_fields=['status'])
            assignment.save(update_fields=['status'])
            messages.success(request, 'Assignment accepted.')
        elif action == 'decline':
            assignment.status = 'DECLINED'
            assignment.order.status = 'DRIVER_PENDING_ASSIGNMENT'
            assignment.order.save(update_fields=['status'])
            assignment.save(update_fields=['status'])
            messages.success(request, 'Assignment declined and returned for reassignment.')
        elif action == 'out_for_delivery':
            assignment.order.status = 'OUT_FOR_DELIVERY'
            assignment.order.save(update_fields=['status'])
            messages.success(request, 'Order marked out for delivery.')
        elif action == 'delivered':
            assignment.status = 'COMPLETED'
            assignment.delivered_at = timezone.now()
            if request.FILES.get('proof_image'):
                assignment.proof_image = request.FILES['proof_image']
            assignment.save()
            assignment.order.status = 'DELIVERED'
            assignment.order.save(update_fields=['status'])
            messages.success(request, 'Delivery completed.')
        return redirect('driver_assignment_detail', assignment_id=assignment.id)
    return render(request, 'drivers_app/assignment_detail.html', {'assignment': assignment})

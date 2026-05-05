from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='driver_dashboard'),
    path('profile/setup/', views.profile_setup, name='driver_profile_setup'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='driver_assignment_detail'),
]

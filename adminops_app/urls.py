from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('orders/', views.order_list, name='admin_order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='admin_order_detail'),
    path('users/', views.user_list, name='admin_user_list'),
    path('disputes/', views.dispute_list, name='admin_disputes'),
]

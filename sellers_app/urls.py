from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='seller_dashboard'),
    path('products/', views.product_list, name='seller_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('orders/', views.order_list, name='seller_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='seller_order_detail'),
    path('stores/add/', views.store_setup, name='seller_store_setup'),
    path('stores/<int:store_id>/edit/', views.store_setup, name='seller_store_edit'),
]

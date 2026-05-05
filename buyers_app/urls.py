from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='buyer_dashboard'),
    path('markets/<int:market_id>/', views.market_products, name='buyer_market_products'),
    path('cart/', views.cart_view, name='buyer_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='buyer_checkout'),
    path('orders/', views.order_history, name='buyer_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='buyer_order_detail'),
    path('orders/<int:order_id>/dispute/', views.create_dispute, name='create_dispute'),
    path('orders/<int:order_id>/rate/', views.create_rating, name='create_rating'),
]

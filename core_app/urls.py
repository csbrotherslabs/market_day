from django.urls import path
from . import views

urlpatterns = [
    path('products/<str:collection>/', views.product_collection, name='product_collection'),
    path('categories/<int:category_id>/', views.category_products, name='category_products'),
    path('markets/<int:market_id>/', views.market_detail, name='market_detail'),
    path('location/update/', views.location_update, name='location_update'),
    path('location/manual-update/', views.manual_location_update, name='manual_location_update'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('markets/<int:market_id>/', views.market_detail, name='market_detail'),
    path('location/update/', views.location_update, name='location_update'),
    path('location/manual-update/', views.manual_location_update, name='manual_location_update'),
]

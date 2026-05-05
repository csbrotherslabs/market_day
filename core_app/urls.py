from django.urls import path
from . import views

urlpatterns = [
    path('markets/<int:market_id>/', views.market_detail, name='market_detail'),
]

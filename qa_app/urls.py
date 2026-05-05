from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='qa_dashboard'),
    path('orders/<int:order_id>/', views.order_review, name='qa_order_review'),
]

from django.contrib import admin
from .models import (
    AdminActionLog, Category, DeliveryAssignment, Dispute, DriverProfile,
    Market, Order, OrderItem, Product, Profile, QAProfile, QAReport,
    Rating, SellerProfile,
)

admin.site.register(Profile)
admin.site.register(Market)
admin.site.register(Category)
admin.site.register(SellerProfile)
admin.site.register(DriverProfile)
admin.site.register(QAProfile)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(QAReport)
admin.site.register(DeliveryAssignment)
admin.site.register(Dispute)
admin.site.register(AdminActionLog)
admin.site.register(Rating)

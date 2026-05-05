from django.contrib.auth.models import User
from django.db import models
from core_app.utils.uploads import delivery_proof_image_path, profile_image_upload_path, qa_inspection_image_path, review_image_path, seller_product_image_path, seller_profile_image_path, seller_store_image_path

class Profile(models.Model):
    ROLE_CHOICES = [('BUYER','Buyer'),('SELLER','Seller'),('DRIVER','Driver'),('QA','QA Analyst'),('ADMIN_STAFF','Admin Staff')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='BUYER')
    phone = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to=profile_image_upload_path, blank=True, null=True)
    theme_preference = models.CharField(max_length=10, default='dark')
    is_verified = models.BooleanField(default=False)
    current_city = models.CharField(max_length=120, blank=True, null=True)
    current_region = models.CharField(max_length=120, blank=True, null=True)
    current_country = models.CharField(max_length=120, blank=True, null=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Market(models.Model):
    name=models.CharField(max_length=255); city=models.CharField(max_length=100); region=models.CharField(max_length=100); country=models.CharField(max_length=120, blank=True, default=''); description=models.TextField(blank=True); latitude=models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True); longitude=models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name=models.CharField(max_length=100, unique=True); active=models.BooleanField(default=True)

class SellerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE); market=models.ForeignKey(Market,on_delete=models.SET_NULL,blank=True,null=True); stall_name=models.CharField(max_length=255,blank=True); stall_number=models.CharField(max_length=100,blank=True); description=models.TextField(blank=True); active=models.BooleanField(default=True); rating_avg=models.DecimalField(max_digits=3, decimal_places=2, default=0); seller_photo=models.ImageField(upload_to=seller_profile_image_path, blank=True, null=True); store_image=models.ImageField(upload_to=seller_store_image_path, blank=True, null=True)

class DriverProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE); vehicle_type=models.CharField(max_length=100,blank=True); license_id=models.CharField(max_length=100,blank=True); region=models.CharField(max_length=100,blank=True); active=models.BooleanField(default=True); rating_avg=models.DecimalField(max_digits=3, decimal_places=2, default=0)

class QAProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE); region=models.CharField(max_length=100,blank=True); active=models.BooleanField(default=True)

class Product(models.Model):
    seller=models.ForeignKey(SellerProfile,on_delete=models.CASCADE,related_name='products'); category=models.ForeignKey(Category,on_delete=models.SET_NULL,blank=True,null=True); name=models.CharField(max_length=255); description=models.TextField(blank=True); price=models.DecimalField(max_digits=10, decimal_places=2); unit=models.CharField(max_length=50, default='piece'); available_qty=models.PositiveIntegerField(default=0); image=models.ImageField(upload_to=seller_product_image_path, blank=True, null=True); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    STATUS_CHOICES=[('CREATED','Created'),('SELLER_CONFIRMED','Seller Confirmed'),('QA_PENDING','QA Pending'),('QA_APPROVED','QA Approved'),('QA_PARTIAL','QA Partial'),('QA_REJECTED','QA Rejected'),('DRIVER_PENDING_ASSIGNMENT','Driver Pending Assignment'),('DRIVER_ASSIGNED','Driver Assigned'),('OUT_FOR_DELIVERY','Out For Delivery'),('DELIVERED','Delivered'),('CANCELLED','Cancelled'),('DISPUTED','Disputed')]
    buyer=models.ForeignKey(User,on_delete=models.CASCADE,related_name='buyer_orders'); market=models.ForeignKey(Market,on_delete=models.SET_NULL,blank=True,null=True); status=models.CharField(max_length=40,choices=STATUS_CHOICES,default='CREATED'); delivery_address=models.CharField(max_length=255); delivery_landmark=models.CharField(max_length=255,blank=True); delivery_phone=models.CharField(max_length=30); subtotal=models.DecimalField(max_digits=10, decimal_places=2, default=0); delivery_fee=models.DecimalField(max_digits=10, decimal_places=2, default=0); total=models.DecimalField(max_digits=10, decimal_places=2, default=0); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items'); product=models.ForeignKey(Product,on_delete=models.CASCADE); seller=models.ForeignKey(SellerProfile,on_delete=models.CASCADE); qty_requested=models.PositiveIntegerField(default=1); qty_approved=models.PositiveIntegerField(blank=True,null=True); unit_price=models.DecimalField(max_digits=10, decimal_places=2); line_total=models.DecimalField(max_digits=10, decimal_places=2)

class QAReport(models.Model):
    RESULT_CHOICES=[('APPROVED','Approved'),('PARTIAL','Partial'),('REJECTED','Rejected')]
    order=models.OneToOneField(Order,on_delete=models.CASCADE); qa_user=models.ForeignKey(User,on_delete=models.CASCADE); result=models.CharField(max_length=20,choices=RESULT_CHOICES); notes=models.TextField(blank=True); inspection_image=models.ImageField(upload_to=qa_inspection_image_path, blank=True, null=True); created_at=models.DateTimeField(auto_now_add=True)

class DeliveryAssignment(models.Model):
    STATUS_CHOICES=[('ASSIGNED','Assigned'),('ACCEPTED','Accepted'),('DECLINED','Declined'),('COMPLETED','Completed')]
    order=models.OneToOneField(Order,on_delete=models.CASCADE); driver=models.ForeignKey(User,on_delete=models.CASCADE); assigned_by=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True,related_name='driver_assignments_created'); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='ASSIGNED'); proof_image=models.ImageField(upload_to=delivery_proof_image_path, blank=True, null=True); delivered_at=models.DateTimeField(blank=True,null=True); created_at=models.DateTimeField(auto_now_add=True)

class Dispute(models.Model):
    STATUS_CHOICES=[('OPEN','Open'),('IN_REVIEW','In Review'),('RESOLVED','Resolved'),('REJECTED','Rejected')]
    order=models.ForeignKey(Order,on_delete=models.CASCADE); opened_by=models.ForeignKey(User,on_delete=models.CASCADE); category=models.CharField(max_length=100); details=models.TextField(); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='OPEN'); resolution_notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)

class AdminActionLog(models.Model):
    admin_user=models.ForeignKey(User,on_delete=models.CASCADE); action_type=models.CharField(max_length=100); target_type=models.CharField(max_length=100); target_id=models.PositiveIntegerField(); details=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE); buyer=models.ForeignKey(User,on_delete=models.CASCADE); seller=models.ForeignKey(SellerProfile,on_delete=models.SET_NULL,null=True,blank=True); driver=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='driver_ratings'); score=models.PositiveSmallIntegerField(default=5); comment=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    reviewer=models.ForeignKey(User,on_delete=models.CASCADE); order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=True); seller=models.ForeignKey(SellerProfile,on_delete=models.SET_NULL,null=True,blank=True); driver=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='driver_reviews'); rating=models.PositiveSmallIntegerField(default=5); comment=models.TextField(blank=True); review_image=models.ImageField(upload_to=review_image_path, blank=True, null=True); created_at=models.DateTimeField(auto_now_add=True)

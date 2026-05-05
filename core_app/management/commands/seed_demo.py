from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core_app.models import Category, DriverProfile, Market, Product, QAProfile, SellerProfile


class Command(BaseCommand):
    help = 'Seeds demo markets, categories, users, and products.'

    def handle(self, *args, **options):
        market1, _ = Market.objects.get_or_create(name='Makola Fresh Market', defaults={'city': 'Accra', 'region': 'Greater Accra', 'description': 'Fresh produce and staples.'})
        market2, _ = Market.objects.get_or_create(name='Kumasi Central Market', defaults={'city': 'Kumasi', 'region': 'Ashanti', 'description': 'Staples and household goods.'})

        for name in ['Vegetables', 'Fruits', 'Grains', 'Spices', 'Fish', 'Household']:
            Category.objects.get_or_create(name=name)

        seller_user, created = User.objects.get_or_create(username='sellerdemo', defaults={'first_name': 'Ama', 'last_name': 'Mensah', 'email': 'seller@example.com'})
        if created:
            seller_user.set_password('password123')
            seller_user.save()
        seller_user.profile.role = 'SELLER'
        seller_user.profile.save()
        seller_profile, _ = SellerProfile.objects.get_or_create(user=seller_user, defaults={'market': market1, 'stall_name': 'Ama Fresh Basket', 'stall_number': 'A12', 'description': 'Trusted family stall'})
        seller_profile.market = market1
        seller_profile.stall_name = seller_profile.stall_name or 'Ama Fresh Basket'
        seller_profile.save()

        driver_user, created = User.objects.get_or_create(username='driverdemo', defaults={'first_name': 'Kojo', 'last_name': 'Boateng', 'email': 'driver@example.com'})
        if created:
            driver_user.set_password('password123')
            driver_user.save()
        driver_user.profile.role = 'DRIVER'
        driver_user.profile.save()
        DriverProfile.objects.get_or_create(user=driver_user, defaults={'vehicle_type': 'Motorbike', 'license_id': 'DRV-001', 'region': 'Accra'})

        qa_user, created = User.objects.get_or_create(username='qademo', defaults={'first_name': 'Esi', 'last_name': 'Owusu', 'email': 'qa@example.com'})
        if created:
            qa_user.set_password('password123')
            qa_user.save()
        qa_user.profile.role = 'QA'
        qa_user.profile.save()
        QAProfile.objects.get_or_create(user=qa_user, defaults={'region': 'Accra'})

        admin_user, created = User.objects.get_or_create(username='admindemo', defaults={'first_name': 'Samuel', 'last_name': 'Admin', 'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})
        if created:
            admin_user.set_password('password123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
        admin_user.profile.role = 'ADMIN_STAFF'
        admin_user.profile.save()

        buyer_user, created = User.objects.get_or_create(username='buyerdemo', defaults={'first_name': 'Akua', 'last_name': 'Buyer', 'email': 'buyer@example.com'})
        if created:
            buyer_user.set_password('password123')
            buyer_user.save()
        buyer_user.profile.role = 'BUYER'
        buyer_user.profile.save()

        vegetables = Category.objects.get(name='Vegetables')
        fruits = Category.objects.get(name='Fruits')
        Product.objects.get_or_create(seller=seller_profile, name='Fresh Tomatoes', defaults={'category': vegetables, 'description': 'Clean red tomatoes', 'price': 18.50, 'unit': 'basket', 'available_qty': 25})
        Product.objects.get_or_create(seller=seller_profile, name='Bell Peppers', defaults={'category': vegetables, 'description': 'Green peppers', 'price': 8.00, 'unit': 'bag', 'available_qty': 40})
        Product.objects.get_or_create(seller=seller_profile, name='Sweet Pineapples', defaults={'category': fruits, 'description': 'Juicy pineapples', 'price': 10.00, 'unit': 'piece', 'available_qty': 20})

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))

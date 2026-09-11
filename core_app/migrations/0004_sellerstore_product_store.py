from django.db import migrations, models
import django.db.models.deletion
import core_app.utils.uploads


def create_initial_stores(apps, schema_editor):
    SellerProfile = apps.get_model('core_app', 'SellerProfile')
    SellerStore = apps.get_model('core_app', 'SellerStore')
    Product = apps.get_model('core_app', 'Product')

    for seller in SellerProfile.objects.all():
        if seller.stall_name or seller.market_id or seller.stall_number or seller.description:
            store = SellerStore.objects.create(
                seller=seller,
                market_id=seller.market_id,
                name=seller.stall_name or f'{seller.user.username} Store',
                stall_number=seller.stall_number,
                description=seller.description,
                store_image=seller.store_image,
                active=seller.active,
            )
            Product.objects.filter(seller=seller, store__isnull=True).update(store=store)


class Migration(migrations.Migration):
    dependencies = [
        ('core_app', '0003_alter_adminactionlog_options_alter_order_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('stall_number', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('store_image', models.ImageField(blank=True, null=True, upload_to=core_app.utils.uploads.seller_store_image_path)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('market', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seller_stores', to='core_app.market')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stores', to='core_app.sellerprofile')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='core_app.sellerstore'),
        ),
        migrations.RunPython(create_initial_stores, migrations.RunPython.noop),
    ]

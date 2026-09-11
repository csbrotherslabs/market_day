from django.db import migrations, models
import core_app.utils.uploads


class Migration(migrations.Migration):
    dependencies = [
        ('core_app', '0004_sellerstore_product_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerstore',
            name='logo_image',
            field=models.ImageField(blank=True, null=True, upload_to=core_app.utils.uploads.seller_store_image_path),
        ),
        migrations.AddField(
            model_name='sellerstore',
            name='template_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='sellerstore',
            name='template_key',
            field=models.CharField(choices=[('fresh_simple', 'Fresh & Simple'), ('boutique', 'Boutique'), ('story_impact', 'Story & Impact'), ('modern_market', 'Modern Market'), ('premium_showcase', 'Premium Showcase'), ('creative_unique', 'Creative & Unique')], default='fresh_simple', max_length=40),
        ),
    ]

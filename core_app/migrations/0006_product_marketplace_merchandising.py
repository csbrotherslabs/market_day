from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0005_sellerstore_template_fields'),
    ]

    operations = [
        migrations.AddField(model_name='product', name='discount_price', field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
        migrations.AddField(model_name='product', name='featured', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='product', name='promoted', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='product', name='is_wholesale', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='product', name='made_in_ghana', field=models.BooleanField(default=False)),
    ]

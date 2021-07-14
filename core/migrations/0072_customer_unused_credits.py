# Generated by Django 3.2.3 on 2021-07-04 06:31

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_adjustment_adjustmentitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='unused_credits',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
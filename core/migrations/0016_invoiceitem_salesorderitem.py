# Generated by Django 3.2.3 on 2021-05-28 07:55

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_invoice_salesorder'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=255)),
                ('cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.salesorder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=255)),
                ('cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.invoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

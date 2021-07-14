# Generated by Django 3.2.3 on 2021-07-04 05:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_auto_20210704_0542'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('description', models.TextField(blank=True)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('payment_note', models.TextField(blank=True)),
                ('gst_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gst_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('net', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('grand_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(blank=True, choices=[('DFT', 'Draft'), ('OP', 'Open')], default='DFT', max_length=3)),
                ('credits_used', models.DecimalField(decimal_places=2, max_digits=10)),
                ('credits_remaining', models.DecimalField(decimal_places=2, max_digits=10)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.company')),
                ('created_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.invoice')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.customer')),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.paymentmethod')),
                ('salesperson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
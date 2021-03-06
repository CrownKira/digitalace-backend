# Generated by Django 3.2.3 on 2021-05-28 08:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20210528_0818'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payslip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('year', models.CharField(max_length=255)),
                ('month', models.CharField(max_length=255)),
                ('basic_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_allowances', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_deductions', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('commission', models.DecimalField(decimal_places=2, max_digits=10)),
                ('commission_amt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('net_pay', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(max_length=255)),
                ('bank', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('comment', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.company')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

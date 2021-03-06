# Generated by Django 3.2.3 on 2021-06-28 02:50

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0060_delete_userconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gst_rate', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('theme', models.CharField(blank=True, choices=[('light', 'light'), ('dark', 'dark')], default='light', max_length=255)),
                ('language', models.CharField(blank=True, choices=[('en', 'en'), ('zh', 'zh')], default='en', max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

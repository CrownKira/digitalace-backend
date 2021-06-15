# Generated by Django 3.2.3 on 2021-06-15 09:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_auto_20210615_0809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productcategory',
            name='agents',
        ),
        migrations.AddField(
            model_name='product',
            name='agents',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]

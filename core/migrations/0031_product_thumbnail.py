# Generated by Django 3.2.3 on 2021-06-08 06:15

import core.models.maintenance
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20210607_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to=core.models.maintenance.product_thumbnail_file_path),
        ),
    ]
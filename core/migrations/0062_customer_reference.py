# Generated by Django 3.2.3 on 2021-06-28 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_userconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='reference',
            field=models.CharField(default='T-0000', max_length=255),
            preserve_default=False,
        ),
    ]
# Generated by Django 3.2.3 on 2021-05-28 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20210528_0909'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='receive',
        ),
        migrations.RemoveField(
            model_name='salesorder',
            name='invoice',
        ),
    ]

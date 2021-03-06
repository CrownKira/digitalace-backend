# Generated by Django 3.2.3 on 2021-07-07 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_creditnote_refund'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creditnote',
            name='payment_date',
        ),
        migrations.RemoveField(
            model_name='creditnote',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='creditnote',
            name='payment_note',
        ),
        migrations.RemoveField(
            model_name='deliveryorder',
            name='payment_date',
        ),
        migrations.RemoveField(
            model_name='deliveryorder',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='deliveryorder',
            name='payment_note',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='payment_date',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='payment_note',
        ),
        migrations.RemoveField(
            model_name='salesorder',
            name='payment_date',
        ),
        migrations.RemoveField(
            model_name='salesorder',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='salesorder',
            name='payment_note',
        ),
    ]

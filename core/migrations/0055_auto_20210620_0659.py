# Generated by Django 3.2.3 on 2021-06-20 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_auto_20210619_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='receiveitem',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salesorderitem',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]

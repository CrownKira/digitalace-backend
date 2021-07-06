# Generated by Django 3.2.3 on 2021-07-04 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_alter_invoice_sales_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(blank=True, choices=[('DFT', 'Draft'), ('PD', 'Paid'), ('UPD', 'Unpaid')], default='DFT', max_length=3),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='status',
            field=models.CharField(blank=True, choices=[('DFT', 'Draft'), ('CP', 'Completed'), ('PD', 'Pending'), ('CC', 'Cancelled')], default='DFT', max_length=3),
        ),
        migrations.AlterField(
            model_name='receive',
            name='status',
            field=models.CharField(blank=True, choices=[('DFT', 'Draft'), ('PD', 'Paid'), ('UPD', 'Unpaid')], default='DFT', max_length=3),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='status',
            field=models.CharField(blank=True, choices=[('DFT', 'Draft'), ('CP', 'Completed'), ('PD', 'Pending'), ('CC', 'Cancelled')], default='DFT', max_length=3),
        ),
    ]

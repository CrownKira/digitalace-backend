# Generated by Django 3.2.3 on 2021-07-05 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0076_alter_creditnote_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditnote',
            name='refund',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]

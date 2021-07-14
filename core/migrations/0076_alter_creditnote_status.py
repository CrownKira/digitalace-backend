# Generated by Django 3.2.3 on 2021-07-05 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_auto_20210705_0419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditnote',
            name='status',
            field=models.CharField(blank=True, choices=[('DFT', 'Draft'), ('OP', 'Open'), ('CL', 'Closed')], default='DFT', max_length=3),
        ),
    ]
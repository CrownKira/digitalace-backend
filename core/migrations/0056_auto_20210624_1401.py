# Generated by Django 3.2.3 on 2021-06-24 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_auto_20210620_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userconfig',
            name='language',
            field=models.CharField(blank=True, choices=[('en', 'en'), ('zh', 'zh')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='userconfig',
            name='theme',
            field=models.CharField(blank=True, choices=[('light', 'light'), ('dark', 'dark')], default='light', max_length=255),
        ),
    ]

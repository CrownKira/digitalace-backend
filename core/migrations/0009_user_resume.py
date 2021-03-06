# Generated by Django 3.2.3 on 2021-05-27 13:51

import core.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='resume',
            field=models.FileField(null=True, upload_to=core.models.user_resume_file_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpeg', 'jpg', 'txt'])]),
        ),
    ]

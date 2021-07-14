# Generated by Django 3.2.3 on 2021-07-04 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_customer_unused_credits'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditNoteItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('credit_note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.creditnote')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
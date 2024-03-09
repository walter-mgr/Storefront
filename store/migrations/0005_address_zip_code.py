# Generated by Django 5.0.1 on 2024-01-21 07:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='zip_code',
            field=models.CharField(default='00000', max_length=5, validators=[django.core.validators.RegexValidator('^\\d{5}$')]),
        ),
    ]

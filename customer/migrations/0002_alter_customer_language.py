# Generated by Django 4.2.7 on 2023-12-07 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='language',
            field=models.TextField(default='Vietnamese'),
        ),
    ]

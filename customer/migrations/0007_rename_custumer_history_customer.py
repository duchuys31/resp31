# Generated by Django 4.2.7 on 2023-12-14 03:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_remove_history_channel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='history',
            old_name='custumer',
            new_name='customer',
        ),
    ]

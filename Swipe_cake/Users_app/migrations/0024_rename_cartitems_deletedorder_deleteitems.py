# Generated by Django 4.2.5 on 2023-10-12 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0023_remove_deletedorder_products_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deletedorder',
            old_name='cartitems',
            new_name='deleteitems',
        ),
    ]

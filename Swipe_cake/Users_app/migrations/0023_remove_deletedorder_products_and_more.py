# Generated by Django 4.2.5 on 2023-10-12 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0022_deletedorderproduct_deletedorder_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deletedorder',
            name='products',
        ),
        migrations.DeleteModel(
            name='DeletedOrderProduct',
        ),
    ]

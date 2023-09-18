# Generated by Django 4.1.7 on 2023-09-15 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0010_product_category_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product_category',
            name='icon',
        ),
        migrations.AddField(
            model_name='product_category',
            name='category_icon',
            field=models.ImageField(null=True, upload_to='category_icons/'),
        ),
    ]

# Generated by Django 4.2.5 on 2023-09-14 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0006_product_category_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_details',
            name='product_image',
            field=models.ImageField(null=True, upload_to='uploads/'),
        ),
    ]

# Generated by Django 4.2.5 on 2023-10-28 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0037_contact_with_us'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 4.2.5 on 2023-09-10 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='custom_users',
            name='otp',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
# Generated by Django 4.1.7 on 2023-09-25 16:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0016_alter_users_address_apartment'),
    ]

    operations = [
        migrations.AddField(
            model_name='users_address',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Users_app.custom_users'),
        ),
    ]

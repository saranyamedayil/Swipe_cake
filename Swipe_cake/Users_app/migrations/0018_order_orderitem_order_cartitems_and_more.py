# Generated by Django 4.2.5 on 2023-10-09 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users_app', '0017_users_address_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')], default='Pending', max_length=50)),
                ('payment_method', models.CharField(choices=[('CashOnDelivery', 'Cash On Delivery'), ('OnlinePayment', 'Online Payment')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('orders', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='orderitems', to='Users_app.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Users_app.product_details')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='cartitems',
            field=models.ManyToManyField(blank=True, to='Users_app.orderitem'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Users_app.users_address'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Users_app.custom_users'),
        ),
    ]
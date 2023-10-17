from django.db import models
import uuid 
from django.utils import timezone


# Create your models here.
# .....................................Signin user details....................................

class Custom_users(models.Model):
    id = models.AutoField(primary_key=True)
    phonenumber=models.CharField(max_length=10,null=True)
    username=models.CharField(max_length=30)
    password=models.CharField(max_length=50,null=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    otp=models.CharField(max_length=6,null=True)
    is_blocked = models.BooleanField(default=False)
    


    def __str__(self) -> str:       
        return self.username
    



    #.................................product details ............................................................................


class Product_Details(models.Model):
    product_id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=255,null=True)
    product_price=models.IntegerField()
    product_image = models.ImageField(upload_to='product_images/', null=True)  # Specify the 'upload_to' directory
    product_quantity=models.FloatField()
    product_descrip=models.CharField(max_length=255,null=True)
    product_stock=models.FloatField()
    # Add a ForeignKey field to link the product to its category
    product_category = models.ForeignKey(
        'Product_Category',
        on_delete=models.CASCADE,
        related_name='products',  # Reverse relationship name
        null=True
    )



    def __str__(self) -> str:       
        return self.product_name



class Product_Category(models.Model):
    category_id=models.AutoField(primary_key=True)
    category_name=models.CharField(max_length=255,null=True)
    Category_quantity=models.FloatField()
    category_icon = models.ImageField(upload_to='category_icons/', null=True)
   



    def __str__(self) -> str:       
        return self.category_name
    


class CartItem(models.Model):
    product = models.ForeignKey(Product_Details, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(Custom_users, on_delete=models.CASCADE, related_name='cart_items')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s cart: {self.quantity} x {self.product.product_name}"
    
    def get_product_image_url(self):
        return self.product.product_image.url if self.product.product_image else ''

    def get_product_name(self):
        return self.product.product_name if self.product else ''
    

class WishlistItem(models.Model):
    user = models.ForeignKey(Custom_users, on_delete=models.CASCADE)
    product = models.ForeignKey(Product_Details, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.product.product_name}"
    
    def get_product_image_url(self):
        return self.product.product_image.url if self.product.product_image else ''

    



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>User address >>>>>>>>>>>>>>>>>>>>>>>....

class Users_Address(models.Model):
    user = models.ForeignKey(Custom_users, on_delete=models.CASCADE,null=True)  # Add a ForeignKey to link to the User model
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)  # Optional field
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255, default='YourDefaultStateValue')  # Default value for 'state'
    zipcode = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return f"{self.user} - {self.first_name} {self.last_name}"
    
    
    




class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CashOnDelivery', 'Cash On Delivery'),
        ('OnlinePayment', 'Online Payment'),
    ]

    user = models.ForeignKey(Custom_users, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'),('Confirm', 'Confirm'), ('Processing', 'Processing'),
                                                       ('Shipped', 'Shipped'), ('Delivered', 'Delivered'),('Cancelled', 'Cancelled')], default='Pending')
    delivery_address = models.ForeignKey(Users_Address, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)  # Payment method field
    cartitems = models.ManyToManyField('OrderItem', blank=True)
    order_number = models.CharField(max_length=100, unique=True,default='000000')
  


    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    product =  models.ForeignKey(Product_Details, on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    orders = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems',default=1)
    unique_order_number = models.CharField(max_length=255,default='0000')  # Add this field to store the unique order number for the product

    def __str__(self):
        # Check if the product attribute is not None before accessing its properties
        if self.product:
            return f"{self.product.product_name} {self.quantity} {self.price}"
        else:
            return f"OrderItem {self.product} (No Product)"
        
    def get_product_image_url(self):
        if self.product and self.product.product_image:
            return self.product.product_image.url
    # If either self.product or self.product.product_image is None, return a default URL or handle it accordingly
        return '/static/default_product_image.jpg'


    
    def save(self, *args, **kwargs):
        # Set the default value for orders as the current user's order
        self.price = self.product.product_price * self.quantity
        current_order = Order.objects.filter(user=self.orders.user).last()
        self.orders = current_order
        super().save(*args, **kwargs)




class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()

    def __str__(self):
        return self.code

    def is_valid(self):
        return timezone.now().date() <= self.expiration_date
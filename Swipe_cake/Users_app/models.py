from django.db import models

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

    


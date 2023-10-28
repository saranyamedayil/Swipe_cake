from django.contrib import admin
from .models import*





def block_users(modeladmin, request, queryset):
    queryset.update(is_blocked=True)

block_users.short_description = "Block selected users"

def unblock_users(modeladmin, request, queryset):
    queryset.update(is_blocked=False)

unblock_users.short_description = "Unblock selected users"

@admin.register(Custom_users)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phonenumber', 'is_blocked', 'is_staff', 'is_superuser')
    list_filter = ('is_blocked', 'is_staff', 'is_superuser')
    actions = [block_users, unblock_users]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'order_date', 'status')
    list_filter = ('status',)


admin.site.register(Product_Details)
admin.site.register(Product_Category)
admin.site.register(CartItem)
admin.site.register(WishlistItem)
admin.site.register(Users_Address)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Category_Offer)
admin.site.register(Product_Offer)
admin.site.register(Message)
admin.site.register(Contact_with_us)
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('user', 'order_date', 'status', 'delivery_address', 'payment_method')
#     list_filter = ('status', 'payment_method')
#     search_fields = ('user__username', 'order_number')

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('product', 'quantity', 'price', 'orders', 'unique_order_number')
#     list_filter = ('orders__status', 'orders__payment_method')
#     search_fields = ('product__product_name', 'orders__user__username')



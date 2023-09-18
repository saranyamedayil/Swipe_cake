from django.contrib import admin
from .models import*



# Register your models here.
# admin.site.register(Custom_users)
# from django.contrib import admin
# from .models import Custom_users
# from .models import Product_Details
# from .models import Product_Category


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


admin.site.register(Product_Details)
admin.site.register(Product_Category)
admin.site.register(CartItem)



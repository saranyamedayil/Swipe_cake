from django import template
from Users_app.models import CartItem  # Replace 'your_app' with the actual app name

register = template.Library()

@register.simple_tag
def cart_total(user):
    cart_items = CartItem.objects.filter(user=user)
    total = sum(item.quantity * item.product.product_price for item in cart_items)
    return total

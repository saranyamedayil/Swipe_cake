from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

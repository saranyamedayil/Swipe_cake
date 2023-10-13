from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
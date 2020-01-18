from django import template

register = template.Library()

@register.filter(name='split')
def split(value):
    print('*************************************')
    print(value)
    return value.split(',')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
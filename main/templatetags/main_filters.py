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
    
@register.filter
def get_item0(dictionary, key):
    print(dictionary)
    print(key)
    return dictionary.get(key)[0]
    
@register.filter
def get_item1(dictionary, key):
    print(dictionary)
    print(key)
    return dictionary.get(key)[1]
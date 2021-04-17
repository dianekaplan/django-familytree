from django import template

register = template.Library()

@register.simple_tag
def generation_class(generation_int):
    return "g" + str(generation_int)
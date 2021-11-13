from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.simple_tag
def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False


@register.simple_tag
def generation_class(generation_int):
    return "g" + str(generation_int)


@register.simple_tag
def get_class(object):
    return object.__class__.__name__


@register.simple_tag
def get_history_filepath(branch):
    result = "familytree/custom/family_history/" + str(branch) + ".html"
    return result


@register.simple_tag
def get_story_filepath(story):
    result = "familytree/custom/stories/" + str(story.slug) + ".html"
    return result


@register.simple_tag
def get_time_ago(datetime):
    time = str(timesince(datetime)).split(",")
    result = time[0] + " ago"
    return result


@register.simple_tag
def get_note_object(object_id):
    result = object_id.split(":")
    if len(result) == 1:
        result = None
    return result[1]

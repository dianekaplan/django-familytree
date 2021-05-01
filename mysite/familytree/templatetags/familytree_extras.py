from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.simple_tag
def generation_class(generation_int):
    return "g" + str(generation_int)


@register.simple_tag
def get_class(object):
    return object.__class__.__name__


@register.simple_tag
def get_history_filepath(branch):
    result = "familytree/family_history/" + str(branch) + ".html"
    return result


@register.simple_tag
def get_story_filepath(story):
    result = "familytree/stories/" + str(story.slug) + ".html"
    return result


@register.simple_tag
def get_outline_filepath(branch):
    result = "familytree/outline_branch_partials/" + str(branch) + "_outline.html"
    return result

@register.simple_tag
def get_time_ago(datetime):
    time = str(timesince(datetime)).split(",")
    result = time[0] + " ago"
    return result


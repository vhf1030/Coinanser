import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def sub(value, arg):
    return value - arg


@register.filter()
def mark(value):
    extensions = ["nl2br", "fenced_code"]
    return mark_safe(markdown.markdown(value, extensions=extensions))


@register.filter()
def get_idx(value, i):
    return value[i]


@register.filter()
def date_convert(dt):
    # return dt.year, dt.month, dt.day, dt.hour, dt.minute
    return dt.year, dt.month, dt.day, dt.hour, dt.minute


@register.filter()
def ranges(count):
    return range(count)



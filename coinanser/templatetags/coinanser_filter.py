import markdown
from django import template
from django.utils.safestring import mark_safe
from coinanser.upbit_api.utils import datetime_convert

register = template.Library()


@register.filter()
def sub(value, arg):
    return value - arg


@register.filter()
def dvd(value, arg):
    return value / arg


@register.filter()
def mtp(value, arg):
    return value * arg


@register.filter()
def rnd(value, arg):
    return round(value, arg)


@register.filter()
def mark(value):
    extensions = ["nl2br", "fenced_code"]
    return mark_safe(markdown.markdown(value, extensions=extensions))


@register.filter()
def get_idx(value, i):
    return value[i]


@register.filter()
def get_keys(dictionary):
    return list(dictionary.keys())


@register.filter()
def date_convert(dt):
    return dt.year, dt.month, dt.day, dt.hour, dt.minute


@register.filter()
def ranges(count):
    return range(count)


@register.filter()
def get_min(li):
    return min(li)


@register.filter()
def get_max(li):
    return max(li)


@register.filter()
def kor_dt_split(dt, arg):
    dc = datetime_convert(dt, to_str=False)
    if arg == 'date':
        return str(dc.date())
    if arg == 'time':
        return str(dc.time())




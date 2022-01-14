import markdown
from django import template
from django.utils.safestring import mark_safe
from coinanser.upbit_api.utils import datetime_convert
from coinanser.upbit_api.get_quotation import MARKET_ALL

register = template.Library()


@register.filter()
def sub(value, arg):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    return value - arg


@register.filter()
def dvd(value, arg):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    return value / arg


@register.filter()
def mtp(value, arg):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    return value * arg


@register.filter()
def pct_rnd(value, arg):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    return str(round(value * 100, arg)) + '%'


@register.filter()
def rnd(value, arg):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    return round(value, arg)


@register.filter()
def sig_fig5(value):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    res = '%.5g' % value
    if value < 10000:
        return float(res)
    else:
        return int(float(res))


@register.filter()
def num_comma(value):
    if value in (None, '') or type(value) not in (int, float):
        return ''
    return format(value, ',')


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
    if dt in (None, ''):
        return ''
    dc = datetime_convert(dt, to_str=False)
    if arg == 'date':
        return str(dc.date())
    if arg == 'time':
        return str(dc.time())


@register.filter()
def market_info(market, arg):
    return MARKET_ALL[market][arg]


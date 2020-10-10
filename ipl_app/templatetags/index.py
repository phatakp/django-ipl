from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def index(iterable, i):
    if iterable:
        return iterable[i]


@register.filter
def prefix(_form):
    return _form.prefix


@register.filter
def split(name):
    return name.split()[0]


@register.filter
def lower(name):
    return name.lower()


@register.filter
def field(form_, f):
    return form_[f]


@register.filter
def errors(field):
    return field.errors


@register.filter
def nferrors(form_):
    return form_.non_field_errors()


@register.filter
def previous_date(iterable, i):
    return iterable[i-1].date


@register.filter
def divide(number, team):
    if team == 'CSK':
        return int(number/2.1)
    elif team == 'DC':
        return int(number/1.7)
    elif team == 'KXIP':
        return int(number/1.4)
    elif team == 'KKR':
        return int(number/1.6)
    elif team == 'MI':
        return int(number/1.7)
    elif team == 'RR':
        return int(number/1.7)
    elif team == 'RCB':
        return int(number/1.9)
    else:
        return int(number/1.8)


@register.filter
def limit(dt):
    return dt < timezone.localtime().date() or (dt == timezone.localtime().date() and timezone.localtime().hour >= 12)


@register.filter
def updated(msg):
    return 'IPL Winner updated to'.lower() in msg.lower()

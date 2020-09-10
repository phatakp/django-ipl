from django import template

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

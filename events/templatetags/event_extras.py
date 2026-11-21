"""Small presentation-only helpers kept out of templates."""

from django import template
from django.http import QueryDict


register = template.Library()


@register.filter
def seat_percent(event):
    """Return a safe 0–100 percentage of an event's occupied capacity."""
    if not event.capacity:
        return 0
    registered = getattr(event, "registration_count", None)
    if registered is None:
        registered = event.registrations.count()
    return max(0, min(100, round((registered / event.capacity) * 100)))


@register.filter
def category_class(value):
    """Turn a category label/code into a conservative CSS class suffix."""
    return str(value).lower().replace(" ", "-")


@register.filter
def add_query_param(querydict, value):
    """Preserve search/filter parameters while pagination changes the page."""
    copied = querydict.copy()
    copied["page"] = value
    return copied.urlencode()


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """Return the current query string with supplied values replaced.

    Django 5.1 also includes a built-in tag with this name, but keeping this
    small version documents the technique and supports the project template.
    """
    request = context.get("request")
    params = request.GET.copy() if request else QueryDict(mutable=True)
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    return params.urlencode()

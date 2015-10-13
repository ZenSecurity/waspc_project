from django.template import Library
from django.utils.safestring import mark_safe
from json import dumps as json_dumps


register = Library()


@register.filter(needs_autoescape=True)
def jsonify(object, autoescape=True):
    return mark_safe(json_dumps(object))

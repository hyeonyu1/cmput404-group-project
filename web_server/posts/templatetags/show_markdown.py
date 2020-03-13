from django import template
from markdownx.utils import markdownify

register = template.Library()

@register.filter
def show_markdown(value):
    return markdownify(value)
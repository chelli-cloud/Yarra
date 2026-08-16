from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """Dict lookup by arbitrary string key (question ids contain dots/hyphens,
    which break Django's built-in `.` template lookup chaining)."""
    if not mapping:
        return None
    return mapping.get(key)

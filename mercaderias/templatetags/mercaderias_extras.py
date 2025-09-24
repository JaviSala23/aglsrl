from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def kg_to_ton(value):
    """Convierte kilogramos a toneladas."""
    try:
        return float(value) / 1000
    except (ValueError, TypeError):
        return value
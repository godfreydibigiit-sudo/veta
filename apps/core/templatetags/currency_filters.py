"""
Custom template filters for currency formatting.
"""
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='tanzanian_shillings')
def tanzanian_shillings(value):
    """
    Format a number as Tanzanian Shillings with commas.
    Examples:
        25000 -> TZS 25,000
        150000 -> TZS 150,000
        0 -> TZS 0
    """
    try:
        value = int(float(value))
        # Format with commas
        formatted = f"{value:,}"
        return f"TZS {formatted}"
    except (ValueError, TypeError):
        return "TZS 0"


@register.filter(name='comma')
def comma_format(value):
    """
    Format a number with commas only (without currency symbol).
    Examples:
        25000 -> 25,000
        150000 -> 150,000
    """
    try:
        value = int(float(value))
        return f"{value:,}"
    except (ValueError, TypeError):
        return "0"


@register.filter(name='short_price')
def short_price(value):
    """
    Format price in shortened form for large numbers.
    Examples:
        25000 -> TZS 25,000
        1500000 -> TZS 1,500,000
    """
    try:
        value = int(float(value))
        return f"TZS {value:,}"
    except (ValueError, TypeError):
        return "TZS 0"
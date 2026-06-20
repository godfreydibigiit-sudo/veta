# 

"""
Custom template filters for currency formatting.
"""
from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()


@register.filter(name='tanzanian_shillings')
def tanzanian_shillings(value):
    """
    Format a number as Tanzanian Shillings with commas.
    Uses Decimal for precise handling.
    
    Examples:
        45000 -> TZS 45,000
        150000 -> TZS 150,000
    """
    try:
        # Convert to Decimal for precision
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            value = Decimal(value)
        
        # Round to 0 decimal places properly
        value = value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
        # Format with commas
        formatted = f"{int(value):,}"
        return f"TZS {formatted}"
    except (ValueError, TypeError, Exception):
        return "TZS 0"


@register.filter(name='comma')
def comma_format(value):
    """
    Format a number with commas only (without currency symbol).
    """
    try:
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            value = Decimal(value)
        
        value = value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return f"{int(value):,}"
    except (ValueError, TypeError, Exception):
        return "0"


@register.filter(name='short_price')
def short_price(value):
    """
    Format price in shortened form for large numbers.
    """
    try:
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            value = Decimal(value)
        
        value = value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return f"TZS {int(value):,}"
    except (ValueError, TypeError, Exception):
        return "TZS 0"
from django import template

register = template.Library()

@register.filter
def format_currency(value):
    """
    Format currency value with comma separators and remove decimal places
    Example: 65000.00 -> 65,000₮
    """
    if value is None:
        return "0₮"
    
    try:
        # Convert to float first to handle Decimal fields
        float_value = float(value)
        
        # Format with comma separators and no decimal places
        formatted = f"{float_value:,.0f}"
        
        # Add currency symbol
        return f"{formatted}₮"
    except (ValueError, TypeError):
        return "0₮"

@register.filter
def format_number(value):
    """
    Format number with comma separators
    Example: 65000 -> 65,000
    """
    if value is None:
        return "0"
    
    try:
        float_value = float(value)
        return f"{float_value:,.0f}"
    except (ValueError, TypeError):
        return "0"

@register.filter
def is_status_completed(order, status_code):
    """
    Check if a specific status has been completed for an order
    """
    return order.is_status_completed(status_code)

@register.filter
def get_status_history(order, status_code):
    """
    Get the first (oldest) status history entry for a specific status
    """
    history = order.status_history.filter(status=status_code).order_by('completed_at').first()
    return history

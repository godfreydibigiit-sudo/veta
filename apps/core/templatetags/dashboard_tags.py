"""
Template tags for dashboard navigation.
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def is_dashboard_active(context, url_name):
    """
    Check if the current URL matches the dashboard URL.
    """
    request = context.get('request')
    if request:
        current = request.resolver_match.url_name if request.resolver_match else ''
        return current == url_name
    return False


@register.simple_tag(takes_context=True)
def get_dashboard_url(context):
    """
    Get the correct dashboard URL based on user role.
    """
    user = context.get('user')
    if user and user.is_authenticated:
        if user.is_manager:
            return '/staff/manager/'
        else:
            return '/staff/'
    return '/staff/'
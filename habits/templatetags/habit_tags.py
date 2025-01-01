from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(str(key))

@register.filter(name='format_duration')
def format_duration(value):
    """
    Format a duration in days
    Usage: {{ value|format_duration }}
    """
    if not value:
        return '0 days'
    return f"{value} {'day' if value == 1 else 'days'}"

@register.filter(name='percentage')
def percentage(value):
    """
    Format a number as a percentage with one decimal place
    Usage: {{ value|percentage }}
    """
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

@register.filter(name='streak_class')
def streak_class(streak_info):
    """
    Return the appropriate CSS class based on streak status
    Usage: {{ streak_info|streak_class }}
    """
    if not streak_info or not streak_info.get('is_active'):
        return 'bg-gray-100 text-gray-800'
    return 'bg-green-100 text-green-800'

@register.simple_tag
def get_streak_status(habit):
    """
    Get the streak status for a habit
    Usage: {% get_streak_status habit as streak %}
    """
    current_streak = habit.get_current_streak()
    longest_streak = habit.get_longest_streak()
    is_active = habit.is_streak_active()
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'is_active': is_active
    }

from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter(name='completion_status')
def completion_status(value):
    """Return CSS class based on completion rate"""
    try:
        rate = float(value)
        if rate >= 80:
            return 'text-green-600'
        elif rate >= 60:
            return 'text-yellow-600'
        elif rate >= 40:
            return 'text-orange-600'
        else:
            return 'text-red-600'
    except (ValueError, TypeError):
        return 'text-gray-600'

@register.filter(name='format_date')
def format_date(date):
    """Format date in readable format"""
    if date:
        return date.strftime("%B %d, %Y")
    return ""

@register.filter(name='completion_rate')
def completion_rate(value):
    """Format completion rate"""
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0%"

@register.filter(name='time_ago')
def time_ago(date):
    """
    Convert a date to "time ago" format
    Usage: {{ date|time_ago }}
    """
    if not date:
        return ''
    
    now = timezone.now()
    diff = now - date

    if diff.days == 0:
        if diff.seconds < 60:
            return 'just now'
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
    elif diff.days == 1:
        return 'yesterday'
    elif diff.days < 7:
        return f"{diff.days}d ago"
    else:
        return date.strftime('%b %d')

@register.simple_tag
def get_completion_summary(habit, days=30):
    """
    Get completion summary for a habit
    Usage: {% get_completion_summary habit as summary %}
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    completions = habit.completions.filter(
        completed_at__date__range=[start_date, end_date]
    ).count()
    
    expected = days if habit.periodicity == 'daily' else (days // 7)
    completion_rate = (completions / expected * 100) if expected > 0 else 0
    
    return {
        'completions': completions,
        'expected': expected,
        'completion_rate': round(completion_rate, 1)
    }

register = template.Library()

@register.filter
def format_duration(value):
    """Format streak duration with proper unit"""
    try:
        days = int(value)
        if days == 1:
            return f"{days} day"
        return f"{days} days"
    except (ValueError, TypeError):
        return "0 days"
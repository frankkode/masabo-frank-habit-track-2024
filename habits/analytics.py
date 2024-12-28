from typing import List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from functools import reduce
from .models import Habit, HabitCompletion

def get_habit_stats(habit: Habit, days: int = 30) -> Dict[str, Any]:
    """Get comprehensive statistics for a single habit"""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    completions = habit.completions.filter(
        completed_at__range=(start_date, end_date)
    )
    
    return {
        'total_completions': completions.count(),
        'streak': habit.get_streak(),
        'completion_rate': habit.get_completion_rate(days),
        'mood_distribution': get_mood_distribution(completions),
        'completion_history': get_completion_history(completions, days),
        'weekday_distribution': get_weekday_distribution(completions),
    }

def get_mood_distribution(completions: List[HabitCompletion]) -> Dict[str, int]:
    """Calculate mood distribution for completions"""
    return (completions
            .exclude(mood='')
            .values('mood')
            .annotate(count=Count('id'))
            .order_by('-count'))

def get_completion_history(completions: List[HabitCompletion], days: int) -> List[Dict[str, Any]]:
    """Generate completion history for the specified period"""
    today = timezone.now().date()
    
    # Create a dictionary of dates with completion counts
    completion_dict = reduce(
        lambda acc, curr: {
            **acc,
            curr.completed_at.date(): acc.get(curr.completed_at.date(), 0) + 1
        },
        completions,
        {}
    )
    
    # Generate date range and map completions
    return [
        {
            'date': (today - timedelta(days=i)).isoformat(),
            'count': completion_dict.get(today - timedelta(days=i), 0)
        }
        for i in range(days)
    ]

def get_weekday_distribution(completions: List[HabitCompletion]) -> Dict[str, int]:
    """Calculate completion distribution by weekday"""
    return (completions
            .values('completed_at__week_day')
            .annotate(count=Count('id'))
            .order_by('completed_at__week_day'))

def get_user_analytics(user, days: int = 30) -> Dict[str, Any]:
    """Get comprehensive analytics for a user"""
    habits = user.habits.all()
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    total_completions = sum(
        habit.completions.filter(
            completed_at__range=(start_date, end_date)
        ).count()
        for habit in habits
    )
    
    return {
        'total_habits': len(habits),
        'habits_by_periodicity': {
            'daily': sum(1 for h in habits if h.periodicity == 'daily'),
            'weekly': sum(1 for h in habits if h.periodicity == 'weekly'),
        },
        'total_completions': total_completions,
        'average_completion_rate': calculate_average_completion_rate(habits, days),
        'top_performing_habits': get_top_performing_habits(habits, days),
        'struggling_habits': get_struggling_habits(habits, days),
        'streak_overview': get_streak_overview(habits),
    }

def calculate_average_completion_rate(habits: List[Habit], days: int) -> float:
    """Calculate average completion rate across all habits"""
    if not habits:
        return 0.0
    
    total_rate = sum(habit.get_completion_rate(days) for habit in habits)
    return total_rate / len(habits)

def get_top_performing_habits(habits: List[Habit], days: int, limit: int = 5) -> List[Dict[str, Any]]:
    """Get habits with highest completion rates"""
    habit_rates = [
        {'habit': habit, 'rate': habit.get_completion_rate(days)}
        for habit in habits
    ]
    return sorted(habit_rates, key=lambda x: x['rate'], reverse=True)[:limit]

def get_struggling_habits(habits: List[Habit], days: int, threshold: float = 50.0) -> List[Habit]:
    """Get habits with completion rates below threshold"""
    return [
        habit for habit in habits
        if habit.get_completion_rate(days) < threshold
    ]

def get_streak_overview(habits: List[Habit]) -> Dict[str, Any]:
    """Get overview of all habit streaks"""
    streaks = [habit.get_streak() for habit in habits]
    return {
        'max_streak': max(streaks, default=0),
        'average_streak': sum(streaks) / len(streaks) if streaks else 0,
        'total_active_streaks': sum(1 for s in streaks if s > 0),
    }

def get_habit_recommendations(user) -> List[Dict[str, str]]:
    """Generate personalized habit recommendations"""
    habits = user.habits.all()
    
    # Basic recommendations based on common categories
    common_habits = [
        {'name': 'Exercise', 'category': 'health'},
        {'name': 'Read', 'category': 'personal_development'},
        {'name': 'Meditate', 'category': 'mindfulness'},
        {'name': 'Journal', 'category': 'reflection'},
        {'name': 'Drink Water', 'category': 'health'},
    ]
    
    # Filter out habits user already has
    existing_habit_names = {habit.name.lower() for habit in habits}
    recommendations = [
        habit for habit in common_habits
        if habit['name'].lower() not in existing_habit_names
    ]
    
    return recommendations[:3]  # Return top 3 recommendations
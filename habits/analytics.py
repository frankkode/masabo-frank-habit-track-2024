from typing import List, Dict, Any
from django.utils import timezone
from django.db.models import Count, Q
from functools import reduce
from .models import Habit, HabitCompletion

# habits/analytics.py
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

class HabitAnalytics:
    def __init__(self, habit):
        self.habit = habit

    def get_completion_rate(self, days=30):
        """Calculate completion rate for the last n days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        completions = self.habit.completions.filter(
            completed_at__range=(start_date, end_date)
        ).count()
        
        expected = days if self.habit.periodicity == 'daily' else days // 7
        if expected == 0:
            return 0
        
        return round((completions / expected) * 100, 2)

    def get_progress_data(self, days=14):
        """Get daily progress data for the specified period"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get all completions within date range
        completions = self.habit.completions.filter(
            completed_at__date__range=(start_date, end_date)
        ).values_list('completed_at__date', flat=True)
        
        # Create daily progress data
        progress_data = []
        current_date = start_date
        
        while current_date <= end_date:
            progress_data.append({
                'date': current_date,
                'completed': current_date in completions,
                'weekday': current_date.strftime('%A')
            })
            current_date += timedelta(days=1)
            
        return progress_data

    def get_longest_streak(self):
        """Calculate the longest streak ever achieved"""
        completions = list(self.habit.completions.order_by(
            'completed_at'
        ).values_list('completed_at__date', flat=True))
        
        if not completions:
            return 0
            
        longest_streak = current_streak = 1
        
        for i in range(1, len(completions)):
            expected_date = completions[i-1] + timedelta(
                days=1 if self.habit.periodicity == 'daily' else 7
            )
            
            if completions[i] == expected_date:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
                
        return longest_streak

    def get_weekly_patterns(self):
        """Analyze completion patterns by day of week"""
        completions = self.habit.completions.all()
        
        # Count completions by weekday
        weekday_counts = defaultdict(int)
        total_weeks = defaultdict(int)
        
        start_date = timezone.now().date() - timedelta(days=90)  # analyze last 90 days
        current_date = timezone.now().date()
        
        # Count total occurrences of each weekday
        while current_date >= start_date:
            total_weeks[current_date.weekday()] += 1
            current_date -= timedelta(days=1)
        
        # Count completions by weekday
        for completion in completions.filter(completed_at__date__gte=start_date):
            weekday = completion.completed_at.weekday()
            weekday_counts[weekday] += 1
        
        # Calculate completion rate for each weekday
        patterns = {}
        for weekday in range(7):
            if total_weeks[weekday] == 0:
                patterns[weekday] = 0
            else:
                patterns[weekday] = round(
                    (weekday_counts[weekday] / total_weeks[weekday]) * 100,
                    2
                )
                
        return patterns

    def get_summary_stats(self):
        """Get summary statistics for the habit"""
        return {
            'total_completions': self.habit.completions.count(),
            'current_streak': self.habit.get_streak(),
            'longest_streak': self.get_longest_streak(),
            'completion_rate': self.get_completion_rate(),
            'weekly_patterns': self.get_weekly_patterns(),
        }
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
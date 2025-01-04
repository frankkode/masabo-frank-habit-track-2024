from django.utils import timezone
from datetime import timedelta

class HabitAnalytics:
    def __init__(self, habit):
        self.habit = habit

    def get_completion_rate(self):
        days = 30
        completions = self.habit.completions.filter(
            completed_at__gte=timezone.now() - timedelta(days=days)
        ).count()
        return (completions / days) * 100

    def get_progress_data(self, days=14):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        completed_dates = set(
            self.habit.completions.filter(
                completed_at__date__gte=start_date,
                completed_at__date__lte=end_date
            ).values_list('completed_at__date', flat=True)
        )
        
        return [
            {'date': start_date + timedelta(days=i), 
             'completed': (start_date + timedelta(days=i)) in completed_dates}
            for i in range(days)
        ]

    def get_longest_streak(self):
        dates = sorted(self.habit.completions.values_list('completed_at__date', flat=True))
        if not dates:
            return 0
            
        max_streak = current_streak = 1
        for i in range(1, len(dates)):
            if dates[i] - dates[i-1] == timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak

    def get_weekly_patterns(self):
        patterns = {i: 0 for i in range(7)}
        completions = self.habit.completions.all()
        total_weeks = 4

        for completion in completions:
            day = completion.completed_at.weekday()
            patterns[day] += (100 / total_weeks)

        return patterns
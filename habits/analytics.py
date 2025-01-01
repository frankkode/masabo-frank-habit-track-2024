from datetime import timedelta, timezone


class HabitAnalytics:
    def __init__(self, habit):
        self.habit = habit

    def get_completion_rate(self) -> float:
        """Calculate completion rate for the last 30 days"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        completions = self.habit.completions.filter(
            completed_at__gte=thirty_days_ago
        ).count()
        
        expected = 30 if self.habit.periodicity == 'daily' else 4
        return round((completions / expected * 100), 1) if expected > 0 else 0

    def get_streak(self) -> int:
        """Calculate current streak"""
        completions = self.habit.completions.order_by('-completed_at')
        if not completions.exists():
            return 0

        streak = 1
        prev_date = completions.first().completed_at.date()
        today = timezone.now().date()

        if prev_date != today and prev_date != today - timedelta(days=1):
            return 0

        for completion in completions[1:]:
            current_date = completion.completed_at.date()
            if (prev_date - current_date).days == 1:
                streak += 1
                prev_date = current_date
            else:
                break

        return streak

    def get_progress_data(self, days=30):
        """Get completion data for the last X days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        completions = set(
            self.habit.completions.filter(
                completed_at__date__gte=start_date,
                completed_at__date__lte=end_date
            ).values_list('completed_at__date', flat=True)
        )
        
        return [{
            'date': start_date + timedelta(days=i),
            'completed': (start_date + timedelta(days=i)) in completions,
            'weekday': (start_date + timedelta(days=i)).strftime('%A')
        } for i in range(days)]
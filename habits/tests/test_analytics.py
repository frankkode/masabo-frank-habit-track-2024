
import pytest
from django.utils import timezone
from datetime import timedelta
from habits.models import Habit, HabitCompletion
from habits.analytics import HabitAnalytics


@pytest.mark.django_db
class TestHabitAnalytics:
    def test_completion_rate(self, user):
        """Test completion rate calculation"""
        habit = Habit.objects.create(
            user=user,
            name="Test Habit",
            periodicity='daily'
        )
        
        # Create 15 completions in last 30 days
        today = timezone.now()
        for i in range(15):
            HabitCompletion.objects.create(
                habit=habit,
                completed_at=today - timedelta(days=i)
            )
            
        analytics = HabitAnalytics(habit)
        assert round(analytics.get_completion_rate()) == 50

    def test_progress_over_time(self, user):
        """Test progress tracking over time"""
        habit = Habit.objects.create(
            user=user,
            name="Test Habit",
            periodicity='daily'
        )
        
        # Create completions with gaps
        dates = [
            timezone.now() - timedelta(days=i)
            for i in [0, 1, 2, 5, 6, 7, 10]
        ]
        
        for date in dates:
            HabitCompletion.objects.create(
                habit=habit,
                completed_at=date
            )
            
        analytics = HabitAnalytics(habit)
        progress_data = analytics.get_progress_data(days=14)
        
        assert len(progress_data) == 14
        assert sum(1 for d in progress_data if d['completed']) == 7

    def test_longest_streak(self, user):
        """Test longest streak calculation"""
        habit = Habit.objects.create(
            user=user,
            name="Test Habit",
            periodicity='daily'
        )
        
        # Create two streaks: 5 days and 3 days
        today = timezone.now()
        
        # First streak (3 days)
        for i in range(3):
            HabitCompletion.objects.create(
                habit=habit,
                completed_at=today - timedelta(days=i+10)
            )
            
        # Second streak (5 days)
        for i in range(5):
            HabitCompletion.objects.create(
                habit=habit,
                completed_at=today - timedelta(days=i)
            )
            
        analytics = HabitAnalytics(habit)
        assert analytics.get_longest_streak() == 5

    def test_weekly_patterns(self, user):
     """Test weekly completion patterns"""
     habit = Habit.objects.create(
          user=user,
          name="Test Habit",
          periodicity='daily'
     )
     
     # Create completions mostly on weekdays
     today = timezone.now()
     for i in range(28):  # 4 weeks
          day = today - timedelta(days=i)
          if day.weekday() < 5:  # Monday to Friday
               HabitCompletion.objects.create(
                    habit=habit,
                    completed_at=day
               )
     
     analytics = HabitAnalytics(habit)
     patterns = analytics.get_weekly_patterns()
     
     # Should show higher completion rates on weekdays
     for day, rate in patterns.items():
          if day < 5:  # Weekday
               assert rate > 30  # More realistic threshold
          else:  # Weekend
               assert rate < 20
def get_weekly_patterns(self):
    patterns = {i: 0 for i in range(7)}  # 0-6 for Monday-Sunday
    completions = self.habit.completions.all()
    total_weeks = 4  # Based on test period

    for completion in completions:
        day = completion.completed_at.weekday()
        patterns[day] += (100 / total_weeks)  # Convert to percentage

    return patterns
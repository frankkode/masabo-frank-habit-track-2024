import pytest
from django.utils import timezone
from datetime import timedelta
from habits.models import Habit, HabitCompletion
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestHabitModel:
    @pytest.fixture
    def user(self):
        User = get_user_model()
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def habit(self, user):
        return Habit.objects.create(
            user=user,
            name='Test Habit',
            periodicity='daily',
            target_completions=1  # Set target to 1 for 100% on first completion
        )

    @pytest.mark.django_db
    def test_completion_percentage(self, daily_habit):
        # Set fixed time for testing
        current_time = timezone.now()
        
        # Create completion for current day
        HabitCompletion.objects.create(
            habit=daily_habit,
            completed_at=current_time
        )
        
        daily_habit.refresh_from_db()
        percentage = daily_habit.get_completion_percentage()
        
        print(f"Target completions: {daily_habit.target_completions}")
        print(f"Total completions: {daily_habit.completions.count()}")
        print(f"Today's completions: {daily_habit.completions.filter(completed_at__date=current_time.date()).count()}")
        print(f"Calculated percentage: {percentage}")
        
        # Assertions
        assert daily_habit.completions.count() == 1
        assert percentage == 100, f"Expected 100%, got {percentage}%"

    def test_weekly_completion_percentage(self, user):
        """Test weekly habit completion percentage"""
        weekly_habit = Habit.objects.create(
            user=user,
            name='Weekly Habit',
            periodicity='weekly',
            target_completions=2
        )
        
        print(f"Initial target completions: {weekly_habit.target_completions}")
        print(f"Initial completion count: {weekly_habit.completions.count()}")
        
        HabitCompletion.objects.create(
            habit=weekly_habit,
            completed_at=timezone.now()
        )
        
        weekly_habit.refresh_from_db()
        percentage = weekly_habit.get_completion_percentage()
        print(f"Final completion count: {weekly_habit.completions.count()}")
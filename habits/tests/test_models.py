from datetime import timedelta
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from habits.models import Habit, HabitCompletion

User = get_user_model()

@pytest.mark.django_db
class TestHabitModel:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @pytest.fixture
    def daily_habit(self, user):
        return Habit.objects.create(
            user=user,
            name='Test Habit',
            periodicity='daily',
            target_completions=1
        )

    def test_completion_percentage(self, daily_habit):
        # Ensure target_completions is correct
        daily_habit.target_completions = 1
        daily_habit.save()

        # Initial percentage should be 0
        assert daily_habit.get_completion_percentage() == 0

        # Create a completion for today
        HabitCompletion.objects.create(
            habit=daily_habit,
            completed_at=timezone.now()  # Ensure it's for today
        )

        # Refresh from db and check percentage
        daily_habit.refresh_from_db()
        assert daily_habit.get_completion_percentage() == 100

    
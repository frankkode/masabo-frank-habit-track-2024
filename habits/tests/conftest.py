# habits/tests/conftest.py

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from habits.models import Habit, HabitCompletion
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def daily_habit(user):
    return Habit.objects.create(
        user=user,
        name='Daily Test',
        periodicity='daily',
        target_completions=1
    )

@pytest.fixture
def weekly_habit(user):
    return Habit.objects.create(
        user=user,
        name='Weekly Test',
        periodicity='weekly',
        target_completions=1
    )

@pytest.fixture
def habit_with_completions(daily_habit):
    dates = [
        timezone.now() - timedelta(days=i) 
        for i in range(5)
    ]
    for date in dates:
        HabitCompletion.objects.create(
            habit=daily_habit,
            completed_at=date
        )
    return daily_habit
@pytest.fixture
def daily_habit(db, user):
    return Habit.objects.create(
        user=user,
        name='Daily Test',
        periodicity='daily',
        target_completions=1
    )
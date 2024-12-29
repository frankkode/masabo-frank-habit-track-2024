import pytest
from django.utils import timezone
from habits.models import Habit, HabitCompletion
from django.contrib.auth import get_user_model

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def authenticated_client(client, user):
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def daily_habit(user):
    return Habit.objects.create(
        user=user,
        name="Test Habit",
        periodicity='daily',
        target_completions=1
    )
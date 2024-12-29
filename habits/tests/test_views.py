import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from habits.models import Habit
from django.utils import timezone

@pytest.mark.django_db
class TestHabitViews:
    @pytest.fixture
    def user(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='12345')
        return user

    @pytest.fixture
    def authenticated_client(self, client, user):
        client.login(username='testuser', password='12345')
        return client

    @pytest.fixture
    def habit(self, user):
        return Habit.objects.create(
            user=user,
            name='Test Habit',
            periodicity='daily',
            target_completions=1
        )

    def test_analytics_view(self, authenticated_client, habit):
        url = reverse('habits:analytics')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_completion_api(self, authenticated_client, habit):
        url = reverse('habits:habit_complete', kwargs={'pk': habit.pk})
        response = authenticated_client.post(url)
        assert response.status_code == 200
        
        habit.refresh_from_db()
        assert habit.completions.count() == 1

    def test_streak_calculation(self, authenticated_client, habit):
        url = reverse('habits:habit_complete', kwargs={'pk': habit.pk})
        response = authenticated_client.post(url)
        
        habit.refresh_from_db()
        assert habit.get_streak() == 1
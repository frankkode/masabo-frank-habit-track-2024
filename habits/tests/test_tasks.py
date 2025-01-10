# habits/tests/test_tasks.py
import pytest
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from habits.models import Habit, HabitCompletion, Notification
from habits.tasks import analyze_habits, send_notification_email
from django.conf import settings

User = get_user_model()

@pytest.mark.django_db
class TestTasks:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @pytest.fixture
    def habit(self, user):
        return Habit.objects.create(
            user=user,
            name='Test Habit',
            periodicity='daily',
            target_completions=1
        )

    @pytest.fixture
    def notification(self, user, habit):
        return Notification.objects.create(
            user=user,
            habit=habit,
            message='Test notification',
            type='reminder'
        )

    @pytest.fixture
    def habit_with_completions(self, habit):
        for i in range(7):
            HabitCompletion.objects.create(
                habit=habit,
                completed_at=timezone.now() - timedelta(days=i)
            )
        return habit

    @patch('habits.tasks.send_mail')  # Change patch path
    def test_send_notification_email(self, mock_send_mail, notification, user):
        mock_send_mail.return_value = 1
        
        result = send_notification_email(
            notification.id,
            user.email,
            "Test Subject"
        )

        mock_send_mail.assert_called_once_with(
            subject="Test Subject",
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        assert result is True

    def test_analyze_habits(self, habit_with_completions):
        notifications_before = Notification.objects.count()
        result = analyze_habits()
        
        assert Notification.objects.count() > notifications_before
        assert result > 0
    
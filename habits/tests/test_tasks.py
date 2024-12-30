from django.test import TestCase
from django.contrib.auth import get_user_model
from habits.models import Habit, Notification
from habits.tasks import send_notification_email, analyze_habits
from unittest.mock import patch, Mock

User = get_user_model()


class TestTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            periodicity='daily'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            habit=self.habit,
            message='Test notification',
            type='reminder'
        )

    @patch('habits.tasks.send_mail')
    def test_send_notification_email(self, mock_send_mail):
        # Set up
        subject = "Test Subject"
        message = "Test Message"
        
        # Call the task
        send_notification_email(
            self.notification.id,
            self.user.email,
            subject
        )

        # Assert the email was sent with correct parameters
        mock_send_mail.assert_called_once_with(
            subject,
            self.notification.message,
            'frankmasabo55@gmail.com',  # Update this to match your settings.DEFAULT_FROM_EMAIL
            [self.user.email],
            fail_silently=False
        )

    @patch('habits.tasks.Notification.objects.create')
    def test_analyze_habits(self, mock_create_notification):
        # Call the task
        analyze_habits()

        # If habit is struggling (completion rate < 50%), a notification should be created
        mock_create_notification.assert_called()

        # Get the call arguments
        call_args = mock_create_notification.call_args[1]
        
        # Assert notification was created with correct parameters
        self.assertEqual(call_args['user'], self.user)
        self.assertEqual(call_args['habit'], self.habit)
        self.assertEqual(call_args['type'], 'reminder')
        self.assertIn('completion rate', call_args['message'].lower())

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Habit,HabitCompletion, Notification
from django.core.mail import send_mail
from django.conf import settings
from .tasks import send_notification_email
# Update habits/apps.py
from django.apps import AppConfig
from .tasks import send_notification_email, analyze_habits


@receiver(post_save, sender=Habit)
def create_habit_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            habit=instance,
            type='reminder',
            message=f'New habit created: {instance.name}'
        )


class HabitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'habits'
@receiver(post_save, sender=HabitCompletion)
def handle_habit_completion(sender, instance, created, **kwargs):
    """Unified handler for habit completion"""
    if created:
        habit = instance.habit
        user = habit.user
        streak = habit.get_streak()

        # Create streak milestone notifications
        if streak in [7, 30, 100]:
            notification = Notification.objects.create(
                user=user,
                habit=habit,
                type='streak',
                message=f'Congratulations! You achieved a {streak}-day streak on {habit.name}!'
            )

            # Send email if user preferences allow
            if user.profile.notification_preferences.get('email_notifications', True):
                send_notification_email.delay(
                    notification_id=notification.id,
                    subject='Habit Streak Achievement!'
                )

        # Send completion notification
        send_notification_email.delay(
            user_id=user.id,
            subject=f'Habit "{habit.name}" completed!',
            message=f'Great job! You completed your habit "{habit.name}".'
        )

        # Trigger analysis
        analyze_habits.delay()
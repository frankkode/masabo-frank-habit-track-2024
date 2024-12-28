
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Habit,HabitCompletion, Notification
# Update habits/apps.py
from django.apps import AppConfig


@receiver(post_save, sender=Habit)
def create_habit_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            habit=instance,
            type='reminder',
            message=f'New habit created: {instance.name}'
        )

@receiver(post_save, sender=HabitCompletion)
def completion_notification(sender, instance, created, **kwargs):
    if created:
        habit = instance.habit
        streak = habit.get_streak()
        
        # Milestone notifications
        if streak in [7, 30, 100]:
            Notification.objects.create(
                user=habit.user,
                habit=habit,
                type='streak',
                message=f'Congratulations! You achieved a {streak}-day streak on {habit.name}!'
            )

class HabitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'habits'

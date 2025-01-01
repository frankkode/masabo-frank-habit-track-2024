from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Habit, Notification, HabitCompletion

@shared_task
def send_notification_email(notification_id, user_email, subject):
    """Send email notification to user"""
    try:
        notification = Notification.objects.get(id=notification_id)
        result = send_mail(
            subject=subject,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False
        )
        return bool(result)
    except Notification.DoesNotExist:
        return False

@shared_task
def analyze_habits():
    """Analyze habits and generate insights"""
    analyzed = False
    habits = Habit.objects.filter(
        completions__completed_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).distinct()
    
    for habit in habits:
        streak = habit.get_streak()
        completion_rate = habit.get_completion_percentage()
        
        if streak >= 7 and completion_rate >= 80:
            Notification.objects.create(
                user=habit.user,
                habit=habit,
                message=f"Great job maintaining {habit.name}! You're on a {streak} day streak!"
            )
            analyzed = True
    return analyzed

@shared_task
def send_habit_reminder():
    today = timezone.now().date()
    incomplete_habits = Habit.objects.filter(
        periodicity='daily'
    ).exclude(
        completions__completed_at__date=today
    )

    for habit in incomplete_habits:
        send_mail(
            subject='Daily Habit Reminder',
            message=f"Don't forget to complete your habit: {habit.name}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[habit.user.email],
            fail_silently=False
        )
    return len(incomplete_habits)
@shared_task
def process_habit_completion(completion_id):
    """Process habit completion and create notifications"""
    try:
        completion = HabitCompletion.objects.get(id=completion_id)
        habit = completion.habit
        streak = habit.get_streak()
        
        if streak in [7, 30, 100]:
            Notification.objects.create(
                user=habit.user,
                habit=habit,
                message=f'Congratulations! You achieved a {streak}-day streak on {habit.name}!'
            )
    except HabitCompletion.DoesNotExist:
        pass
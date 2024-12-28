
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Habit, Notification
from django.core.mail import send_mail

@shared_task
def send_notification_email(user_id, subject, message):
    user = User.objects.get(id=user_id)
    if user.profile.notification_preferences.get('email_notifications'):
        send_mail(subject, message, 'from@example.com', [user.email])

@shared_task
def analyze_habits():
    """Daily analysis of habits"""
    for habit in Habit.objects.all():
        # Check for broken streaks
        if habit.get_streak() == 0:
            last_completion = habit.completions.order_by('-completed_at').first()
            if last_completion:
                days_since = (timezone.now() - last_completion.completed_at).days
                if days_since > (1 if habit.periodicity == 'daily' else 7):
                    Notification.objects.create(
                        user=habit.user,
                        habit=habit,
                        type='break',
                        message=f'Your streak for {habit.name} was broken. Time to start again!'
                    )
        
        # Check for struggling habits
        completion_rate = habit.get_completion_rate()
        if completion_rate < 50:
            Notification.objects.create(
                user=habit.user,
                habit=habit,
                type='reminder',
                message=f'Your completion rate for {habit.name} is low. Need help getting back on track?'
            )

# Add to celery beat schedule in settings.py
CELERY_BEAT_SCHEDULE = {
    'analyze-habits': {
        'task': 'habits.tasks.analyze_habits',
        'schedule': timedelta(days=1),
    },
}
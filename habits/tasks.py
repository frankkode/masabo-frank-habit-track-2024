
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Habit, Notification

@shared_task
def send_notification_email(notification_id, user_email, subject):
    """Send notification email to user"""
    try:
        notification = Notification.objects.get(id=notification_id)
        send_mail(
            subject,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@shared_task
def analyze_habits():
    """Analyze habits and create notifications for struggling habits"""
    notifications_created = 0
    
    for habit in Habit.objects.all():
        try:
            # Check completion rate
            completion_rate = habit.get_completion_rate()
            
            if completion_rate < 50:
                # Create notification for struggling habits
                Notification.objects.create(
                    user=habit.user,
                    habit=habit,
                    type='reminder',
                    message=f'Your completion rate for {habit.name} is low ({completion_rate}%). Need help getting back on track?'
                )
                notifications_created += 1

            # Check for broken streaks
            if habit.get_streak() == 0:
                last_completion = habit.completions.order_by('-completed_at').first()
                if last_completion:
                    days_since = (timezone.now() - last_completion.completed_at).days
                    expected_interval = 1 if habit.periodicity == 'daily' else 7
                    
                    if days_since > expected_interval:
                        Notification.objects.create(
                            user=habit.user,
                            habit=habit,
                            type='break',
                            message=f'Your streak for {habit.name} was broken. Time to start again!'
                        )
                        notifications_created += 1

        except Exception as e:
            print(f"Error analyzing habit {habit.id}: {e}")
            continue

    return notifications_created

# Add to celery beat schedule in settings.py
CELERY_BEAT_SCHEDULE = {
    'analyze-habits': {
        'task': 'habits.tasks.analyze_habits',
        'schedule': timedelta(days=1),
    },
}
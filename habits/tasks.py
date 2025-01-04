from venv import logger
import logging
from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Habit, Notification, HabitCompletion
from django.contrib.auth.models import User





User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def send_notification_email(user_id, subject, message, notification_type='email'):
    logger.info(f"Starting email task for user {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Found user: {user.email}")
        
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            message=message
        )
        logger.info(f"Created notification: {notification.id}")

        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        logger.info(f"Email sent: {result}")

        return result
    except Exception as e:
        logger.error(f"Error in send_notification_email: {str(e)}")
        return False

@shared_task
def analyze_habits():
    """Analyze habits and create notifications for struggling habits"""
    logger.info("Starting habit analysis")
    notification_count = 0
    
    try:
        habits = Habit.objects.select_related('user').all()
        
        for habit in habits:
            if habit.get_completion_percentage() < 50:
                message = f"Your habit '{habit.name}' needs attention"
                send_notification_email.delay(
                    user_id=habit.user.id,
                    subject="Habit Needs Attention",
                    message=message,
                    notification_type='alert'
                )
                notification_count += 1
                
        logger.info(f"Completed analysis. Created {notification_count} notifications")
        return notification_count
    except Exception as e:
        logger.error(f"Error in analyze_habits: {str(e)}")
        return 0

@shared_task
def send_habit_reminder():
    """Send daily reminders for incomplete habits"""
    logger.info("Starting daily reminders")
    reminder_count = 0
    today = timezone.now().date()
    
    try:
        habits = Habit.objects.select_related('user').filter(
            periodicity='daily',
            user__profile__notification_preferences__daily_reminders=True
        ).exclude(
            completions__completed_at__date=today
        )

        for habit in habits:
            message = f"Don't forget to complete your habit: {habit.name}"
            send_notification_email.delay(
                user_id=habit.user.id,
                subject="Daily Habit Reminder",
                message=message,
                notification_type='reminder'
            )
            reminder_count += 1

        logger.info(f"Sent {reminder_count} reminders")
        return reminder_count
    except Exception as e:
        logger.error(f"Error in send_habit_reminder: {str(e)}")
        return 0
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
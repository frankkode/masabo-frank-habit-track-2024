import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habit_tracker.settings')

app = Celery('habit_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-daily-habits': {
        'task': 'habits.tasks.send_habit_reminder',
        'schedule': crontab(hour=21, minute=43),  # Run daily at 8 PM
    },
    'analyze-habits': {
        'task': 'habits.tasks.analyze_habits',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}
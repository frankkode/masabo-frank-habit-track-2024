import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habit_tracker.settings')

app = Celery('habit_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-habit-streaks': {
        'task': 'habits.tasks.check_habit_streaks',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'check-pending-habits': {
        'task': 'habits.tasks.check_pending_habits',
        'schedule': crontab(minute=0, hour=20),
    },
    'check-broken-streaks': {
        'task': 'habits.tasks.check_broken_streaks',
        'schedule': crontab(minute=0, hour=0),
    },
}
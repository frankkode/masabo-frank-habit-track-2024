from datetime import datetime, time
from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from habits.streak_utils import StreakCalculator
import pytz

User = get_user_model()

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = CloudinaryField('avatar', blank=True, null=True
    )
    bio = models.TextField(max_length=500, blank=True)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default='UTC'
    )
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='system'
    )
    notification_preferences = models.JSONField(
        default=dict,
        help_text="User notification preferences",
        blank=True, 
    )
    daily_reminder_time = models.TimeField(null=True, blank=True)
    weekly_report = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_notification_settings(self):
        """Get current notification settings with defaults"""
        defaults = {
            'email_notifications': True,
            'daily_reminders': True,
            'weekly_summary': self.weekly_report
        }
        return {**defaults, **self.notification_preferences}

    def update_notification_settings(self, settings):
        """Update notification preferences"""
        self.notification_preferences.update(settings)
        
        # Handle daily reminder time based on settings
        if not settings.get('daily_reminders', False):
            self.daily_reminder_time = None
        elif not self.daily_reminder_time:
            self.daily_reminder_time = time(9, 0)
            
        self.save()

    def clean(self):
        """Validate model fields"""
        super().clean()
        if not self.notification_preferences.get('daily_reminders', False):
            self.daily_reminder_time = None
        elif self.notification_preferences.get('daily_reminders', False) and not self.daily_reminder_time:
            self.daily_reminder_time = time(9, 0)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Notification(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habit_notifications')
   message = models.CharField(max_length=255)
   is_read = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)
   notification_type = models.CharField(max_length=50, blank=True)
   reference_id = models.IntegerField(null=True, blank=True)
   def get_streak(self):
        calculator = StreakCalculator(self)
        return calculator.calculate_current_streak()

   def get_streak_details(self):
        calculator = StreakCalculator(self)
        return calculator.get_streak_details()
   class Meta:
       ordering = ['-created_at']

   def __str__(self):
       return f"{self.user.username} - {self.message[:50]}"
   @classmethod
   def get_unread_for_user(cls, user):
        return cls.objects.filter(user=user, is_read=False)

   @classmethod
   def mark_all_read(cls, user):
        return cls.objects.filter(user=user, is_read=False).update(is_read=True)
   def clean(self):
    """Validate model fields"""
    super().clean()
    # Only validate daily_reminder_time if it's set
    if not self.notification_preferences.get('daily_reminders', False):
        # If daily reminders are disabled, clear the reminder time
        self.daily_reminder_time = None


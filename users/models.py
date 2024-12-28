from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import pytz

User = get_user_model()

class UserProfile(models.Model):
   THEME_CHOICES = [
       ('light', 'Light'),
       ('dark', 'Dark'),
       ('system', 'System')
   ]
   
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
   avatar = models.ImageField(
       upload_to='avatars/',
       null=True, 
       blank=True,
       default='avatars/default.png'
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
       help_text="User notification preferences"
   )
   daily_reminder = models.TimeField(null=True, blank=True)
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
        self.save()
   def clean(self):
       if self.daily_reminder_time and not self.notification_preferences.get('daily_reminders'):
           raise ValidationError('Daily reminder time set but daily reminders are disabled')

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

   class Meta:
       ordering = ['-created_at']

   def __str__(self):
       return f"{self.user.username} - {self.message[:50]}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
   if created:
       UserProfile.objects.create(user=instance)
   else:
       UserProfile.objects.get_or_create(user=instance)
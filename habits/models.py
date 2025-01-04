from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

User = get_user_model()

class Habit(models.Model):
    """Model for tracking user habits and their completion status."""
    
    PERIODICITY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    periodicity = models.CharField(max_length=10, choices=PERIODICITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=timezone.now)
    color = models.CharField(max_length=7, default="#3B82F6")
    target_completions = models.PositiveIntegerField(
        help_text="Number of times to complete this habit"
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_periodicity_display()})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            # Set target completions based on periodicity
            self.target_completions = 30 if self.periodicity == 'daily' else 4
        super().save(*args, **kwargs)

    def clean(self):
        """Validate color format."""
        if not self.color.startswith('#'):
            raise ValidationError('Color must be a valid hex code starting with #')
        if len(self.color) != 7:
            raise ValidationError('Color must be in #RRGGBB format')

    def get_progress_text(self):
        """Get formatted progress text"""
        completions = self.completions.count()
        target = self.target_completions
        return f"{completions}/{target}"

    def get_completion_percentage(self):
        today = timezone.now().date()
        daily_completions = self.completions.filter(
            completed_at__date=today,
        ).count()
        return 100 if daily_completions >= self.target_completions else 0
    def is_completed(self):
        """Check if habit has reached its target completions"""
        return self.completions.count() >= self.target_completions
    def get_next_due_date(self):
        """Calculate next due date based on periodicity"""
        last_completion = self.completions.order_by('-completed_at').first()
        now = timezone.now()
        
        if not last_completion:
            return now
            
        last_date = last_completion.completed_at
        
        if self.periodicity == 'daily':
            next_due = last_date + timedelta(days=1)
        else:  # weekly
            next_due = last_date + timedelta(weeks=1)
            
        # If next due date is in the past, return current time
        return next_due if next_due > now else now

    def get_completion_percentage(self):
        """Calculate completion percentage for today"""
        today = timezone.now().date()
        daily_completions = self.completions.filter(
            completed_at__date=today
        ).count()
        return 100 if daily_completions > 0 else 0
    # Streak Methods
    def get_streak(self):
        """Calculate current streak taking periodicity into account"""
        completions = self.completions.order_by('-completed_at')
        if not completions.exists():
            return 0
        
        today = timezone.now().date()
        last_completion = completions.first().completed_at.date()
        
        # Check if streak is broken
        if self.periodicity == 'daily':
            if (today - last_completion).days > 1:
                return 0
        else:  # weekly
            if (today - last_completion).days > 7:
                return 0
        
        # Calculate streak
        streak = 1
        prev_date = last_completion
        
        for completion in completions[1:]:
            current_date = completion.completed_at.date()
            expected_gap = 1 if self.periodicity == 'daily' else 7
            
            if (prev_date - current_date).days == expected_gap:
                streak += 1
                prev_date = current_date
            else:
                break
        
        return streak

    # Alias for backward compatibility
    def get_current_streak(self):
        """Alias for get_streak()"""
        return self.get_streak()
    
    
    def get_longest_streak(self):
        """Calculate longest streak ever achieved"""
        completions = list(self.completions.order_by('completed_at'))
        if not completions:
            return 0

        longest_streak = current_streak = 1
        expected_gap = 1 if self.periodicity == 'daily' else 7

        for i in range(1, len(completions)):
            current_date = completions[i].completed_at.date()
            prev_date = completions[i-1].completed_at.date()
            
            if (current_date - prev_date).days == expected_gap:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return longest_streak
    def get_last_completion(self):
        """Get the most recent completion date"""
        last_completion = self.completions.order_by('-completed_at').first()
        if last_completion:
            return last_completion.completed_at.isoformat()
        return None

    def get_completion_status(self):
        """Check if habit is completed for current period"""
        last_completion = self.get_last_completion()
        if not last_completion:
            return False
            
        now = timezone.now()
        completion_date = timezone.datetime.fromisoformat(last_completion)
        
        if self.periodicity == 'daily':
            return completion_date.date() == now.date()
        else:  # weekly
            week_start = now - timedelta(days=now.weekday())
            return completion_date.date() >= week_start.date()

    def get_completion_rate(self, days=30):
        """Calculate completion rate for the specified period"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        completions = self.completions.filter(
            completed_at__date__range=[start_date, end_date]
        ).count()
        
        if self.periodicity == 'daily':
            expected = days  # One completion per day
        else:
            expected = days // 7  # One completion per week
            
        if expected == 0:
            return 0.0
        
        rate = (completions / expected) * 100
        return round(min(rate, 100), 1)

    def get_stats(self):
        """Get habit statistics including historical data."""
        total_completions = self.completions.count()
        cycles_completed = total_completions // self.target_completions
        return {
            'total_completions': total_completions,
            'cycles_completed': cycles_completed,
            'current_cycle': self.get_completion_percentage(),
            'current_streak': self.get_current_streak()
        }

    def complete_habit(self):
        """Complete habit and handle milestone/streak notifications."""
        completion = HabitCompletion.objects.create(
            habit=self,
            completed_at=timezone.now()
        )
        
        self.handle_streak_completion()
        return completion

    def handle_streak_completion(self):
        """Handle streak achievements and create notifications."""
        current_streak = self.get_current_streak()
        milestones = [7, 30, 60, 90, 180, 365]
        
        for milestone in milestones:
            if current_streak == milestone:
                Notification.objects.create(
                    user=self.user,
                    habit=self,
                    type='streak',
                    message=f"Congratulations! You've maintained a {milestone}-day streak for {self.name}!"
                )
                return True
        return False

class HabitCompletion(models.Model):
    """Model for tracking individual habit completions."""
    
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True)
    mood = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-completed_at']
        get_latest_by = 'completed_at'

    def __str__(self):
        return f"{self.habit.name} completed at {self.completed_at}"

class Notification(models.Model):
    """Model for tracking user notifications."""
    
    NOTIFICATION_TYPES = [
        ('reminder', 'Reminder'),
        ('streak', 'Streak Achievement'),
        ('break', 'Streak Break'),
        ('milestone', 'Milestone'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} for {self.habit.name}"

    def mark_as_read(self):
        self.read = True
        self.save()

@receiver(post_save, sender=User)
def create_default_habits(sender, instance, created, **kwargs):
    """Create default habits for new users."""
    if created:
        default_habits = [
            {
                'name': 'Exercise',
                'description': 'Stay active with daily exercise',
                'periodicity': 'daily',
                'color': '#3B82F6'
            },
            {
                'name': 'Read',
                'description': 'Read for at least 30 minutes',
                'periodicity': 'daily',
                'color': '#10B981'
            },
            {
                'name': 'Clean House',
                'description': 'Weekly house cleaning routine',
                'periodicity': 'weekly',
                'color': '#8B5CF6'
            }
        ]
        
        for habit_data in default_habits:
            Habit.objects.create(user=instance, **habit_data)
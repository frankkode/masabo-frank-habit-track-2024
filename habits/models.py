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
        """Set default target completions on creation."""
        if not self.pk:  # Only on creation
            self.target_completions = 4 if self.periodicity == 'weekly' else 30
        super().save(*args, **kwargs)

    def clean(self):
        """Validate color format."""
        if not self.color.startswith('#'):
            raise ValidationError('Color must be a valid hex code starting with #')
        if len(self.color) != 7:
            raise ValidationError('Color must be in #RRGGBB format')

    # Progress and Completion Methods
    def get_progress(self):
        """Calculate progress percentage based on periodicity."""
        if self.periodicity == 'weekly':
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            weekly_completions = self.completions.filter(
                completed_at__date__gte=week_start
            ).count()
            return min((weekly_completions / 4) * 100, 100)
        return self.get_completion_percentage()

    def get_completion_percentage(self):
        """Calculate completion percentage."""
        completed = self.completions.count()
        return min(round((completed / self.target_completions) * 100), 100)

    def get_completion_status(self):
        """Check if habit is completed for current period."""
        now = timezone.now()
        latest_completion = self.completions.order_by('-completed_at').first()
        
        if not latest_completion:
            return False
            
        if self.periodicity == 'daily':
            return latest_completion.completed_at.date() == now.date()
            
        week_start = now - timedelta(days=now.weekday())
        return latest_completion.completed_at.date() >= week_start.date()

    def get_completion_rate(self, days=30):
        """Calculate completion rate for given period."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        completions = self.completions.filter(
            completed_at__range=(start_date, end_date)
        ).count()
        
        expected = days if self.periodicity == 'daily' else days // 7
        return (completions / expected * 100) if expected > 0 else 0

    # Streak Methods
    def get_streak(self):
        """Calculate current streak."""
        completions = self.completions.order_by('-completed_at')
        if not completions.exists():
            return 0
            
        current_streak = 1
        last_completion = completions.first()
        last_date = last_completion.completed_at.date()
        
        for completion in completions[1:]:
            completion_date = completion.completed_at.date()
            expected_date = (
                last_date - timedelta(days=1)
                if self.periodicity == 'daily'
                else last_date - timedelta(weeks=1)
            )
            
            if completion_date == expected_date:
                current_streak += 1
                last_date = completion_date
            else:
                break
                
        return current_streak

    def handle_streak_completion(self):
        """Handle streak achievements and create notifications."""
        current_streak = self.get_streak()
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

    def break_streak(self):
        """Handle streak break notifications."""
        if self.get_streak() > 7:
            Notification.objects.create(
                user=self.user,
                habit=self,
                type='break',
                message=f'Oh no! You broke your streak for {self.name}. Keep going!'
            )

    # Completion Methods
    def complete_habit(self):
        """Complete habit and handle streak logic."""
        completion = HabitCompletion.objects.create(
            habit=self,
            completed_at=timezone.now()
        )
        self.handle_streak_completion()
        return completion

    def get_next_due_date(self):
        """Calculate next due date based on periodicity."""
        last_completion = self.completions.order_by('-completed_at').first()
        if not last_completion:
            return timezone.now()
            
        if self.periodicity == 'daily':
            return last_completion.completed_at + timedelta(days=1)
        return last_completion.completed_at + timedelta(weeks=1)

    def is_completed(self):
        """Check if habit has reached target completions."""
        return self.completions.count() >= self.target_completions
    def get_completion_percentage(self):
        """Calculate completion percentage with reset after target."""
        total_completions = self.completions.count()
        cycles_completed = total_completions // self.target_completions
        current_cycle_completions = total_completions % self.target_completions
        
        # Calculate percentage for current cycle
        return min(round((current_cycle_completions / self.target_completions) * 100), 100)

    def get_stats(self):
        """Get habit statistics including historical data."""
        total_completions = self.completions.count()
        cycles_completed = total_completions // self.target_completions
        return {
            'total_completions': total_completions,
            'cycles_completed': cycles_completed,
            'current_cycle': self.get_completion_percentage(),
            'current_streak': self.get_streak()
        }

    def complete_habit(self):
        """Complete habit and handle reset logic."""
        completion = HabitCompletion.objects.create(
            habit=self,
            completed_at=timezone.now()
        )
        
        # Check if target reached for notifications
        if (self.completions.count() % self.target_completions) == 0:
            Notification.objects.create(
                user=self.user,
                habit=self,
                type='milestone',
                message=f"Congratulations! You've completed another cycle of {self.name}!"
            )
            
        self.handle_streak_completion()
        return completion


class HabitCompletion(models.Model):
    """Model for tracking individual habit completions."""
    
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True)
    mood = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-completed_at']

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
            
        
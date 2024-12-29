from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from .models import Habit, HabitCompletion, Notification
from django.views.generic import TemplateView
import json
from .forms import HabitForm, HabitCompletionForm
from datetime import timedelta


class BaseView(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(
            user=self.request.user,
            read=False
        ).order_by('-created_at')[:5]
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'habits/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_habits = Habit.objects.filter(user=self.request.user)
        today = timezone.now().date()
        
        # Calculate total completions
        total_completions = sum(
            habit.completions.count() 
            for habit in user_habits
        )
        
        # Calculate longest streak
        longest_streak = max(
            (habit.get_streak() for habit in user_habits),
            default=0
        )

        context.update({
            'total_habits': user_habits.count(),
            'total_completions': total_completions,
            'longest_streak': longest_streak,
            'completed_today': self.get_completed_today(user_habits, today),
            'daily_habits': user_habits.filter(periodicity='daily'),
            'weekly_habits': user_habits.filter(periodicity='weekly'),
            'habits': user_habits,
        })
        return context

    def get_completed_today(self, habits, today):
        """Calculate habits completed today"""
        return habits.filter(
            completions__completed_at__date=today
        ).distinct().count()

    def get_current_streak(self, habits):
        """Calculate current streak across all habits"""
        if not habits.exists():
            return 0
        
        return max(
            (habit.get_streak() for habit in habits),
            default=0
        )
    def get_statistics(self):
        """Calculate dashboard statistics"""
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        habits = self.get_queryset()
        
        completions = HabitCompletion.objects.filter(
            habit__in=habits,
            completed_at__gte=thirty_days_ago
        )
        
        total_completions = completions.count()
        current_streaks = {
            habit.id: habit.get_streak() 
            for habit in habits
        }
        
        return {
            'total_habits': habits.count(),
            'total_completions': total_completions,
            'longest_streak': max(current_streaks.values(), default=0),
            'completion_rate': self.calculate_completion_rate(habits),
            'streaks': current_streaks
        }
    
    def calculate_completion_rate(self, habits):
        """Calculate overall completion rate for the last 30 days"""
        if not habits:
            return 0
            
        total_required = sum(
            30 if habit.periodicity == 'daily' else 4
            for habit in habits
        )
        
        if total_required == 0:
            return 0
            
        thirty_days_ago = timezone.now() - timedelta(days=30)
        total_completed = HabitCompletion.objects.filter(
            habit__in=habits,
            completed_at__gte=thirty_days_ago
        ).count()
        
        return round((total_completed / total_required) * 100, 1)
    def get_weekly_progress(self):
        from datetime import datetime, timedelta
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        completions_this_week = self.completions.filter(date__gte=week_ago).count()
        return min((completions_this_week / self.target_completions) * 100, 100)
def notifications(request):
    if request.user.is_authenticated:
        return {
            'notifications': request.user.notifications.filter(
                read=False
            ).order_by('-created_at')[:5]
        }
    return {'notifications': []}

class HabitCreateView(LoginRequiredMixin, CreateView):
    """Create a new habit"""
    model = Habit
    form_class = HabitForm
    template_name = 'habits/habit_form.html'
    success_url = reverse_lazy('habits:dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Habit created successfully!')
        return super().form_valid(form)

class HabitUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing habit"""
    model = Habit
    form_class = HabitForm
    template_name = 'habits/habit_form_update.html'
    success_url = reverse_lazy('habits:dashboard')
    
    def get_queryset(self):
        # Ensure user can only update their own habits
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        # Keep the original user when updating
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Habit updated successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True  # To differentiate between create and update in template
        context['title'] = 'Update Habit'
        return context
class HabitDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a habit"""
    model = Habit
    success_url = reverse_lazy('habits:dashboard')
    template_name = 'habits/habit_confirm_delete.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Habit deleted successfully!')
        return super().delete(request, *args, **kwargs)

class HabitDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single habit"""
    model = Habit
    template_name = 'habits/habit_detail.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habit = self.object
        
        # Get completion history
        context['completions'] = habit.completions.all()[:30]
        context['completion_form'] = HabitCompletionForm()
        
        # Calculate statistics
        context['current_streak'] = habit.get_streak()
        context['completion_rate'] = habit.get_completion_rate()
        
        # Get completion history for chart
        context['completion_history'] = self.get_completion_history(habit)
        
        return context
    
    def get_completion_history(self, habit):
        """Get completion history for the last 30 days"""
        today = timezone.now().date()
        history = []
        
        for i in range(30):
            date = today - timedelta(days=i)
            completions = habit.completions.filter(
                completed_at__date=date
            ).count()
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': completions
            })
        
        return list(reversed(history))

class HabitCompletionView(LoginRequiredMixin, View):
    """Handle habit completion"""
    
    def post(self, request, pk):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)
        form = HabitCompletionForm(request.POST)
        
        if form.is_valid():
            completion = form.save(commit=False)
            completion.habit = habit
            completion.save()
            
            # Check for streak achievements
            streak = habit.get_streak()
            if streak in [7, 30, 100]:
                Notification.objects.create(
                    user=request.user,
                    habit=habit,
                    type='streak',
                    message=f'Congratulations! {streak}-day streak on {habit.name}!'
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Habit completed successfully!',
                'streak': streak
            })
        
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid form data.'
        }, status=400)

class NotificationListView(LoginRequiredMixin, ListView):
    """View all notifications"""
    model = Notification
    template_name = 'habits/notifications.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MarkNotificationReadView(LoginRequiredMixin, View):
    """Mark notification as read"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')
            notification = get_object_or_404(
                Notification, 
                id=notification_id, 
                user=request.user
            )
            notification.mark_as_read()
            return JsonResponse({
                'status': 'success',
                'message': 'Notification marked as read'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Notification.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Notification not found'
            }, status=404)


class BulkHabitCompletionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            habit_ids = data.get('habit_ids', [])
            date = data.get('date', timezone.now().date().isoformat())
            
            completions = []
            for habit_id in habit_ids:
                habit = Habit.objects.get(id=habit_id, user=request.user)
                completion, created = HabitCompletion.objects.get_or_create(
                    habit=habit,
                    date=date
                )
                completions.append({
                    'habit_id': habit_id,
                    'completed': True,
                    'date': date
                })
                
            return JsonResponse({
                'status': 'success',
                'completions': completions
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

class HabitAnalyticsView(LoginRequiredMixin, View):
    def get(self, request, habit_id):
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        analytics = HabitAnalytics(habit)
        
        response_data = {
            'habit_id': habit.id,
            'name': habit.name,
            'analytics': {
                'completion_rate': analytics.get_completion_rate(),
                'total_completions': habit.completions.count(),
                'current_streak': habit.get_streak(),
                'longest_streak': analytics.get_longest_streak(),
                'progress_data': analytics.get_progress_data(days=30),
                'weekly_patterns': analytics.get_weekly_patterns()
            }
        }

        # Add detailed completion history
        completion_history = []
        for data in analytics.get_progress_data(days=30):
            completion_history.append({
                'date': data['date'].isoformat(),
                'completed': data['completed'],
                'weekday': data['weekday']
            })
        
        response_data['completion_history'] = completion_history

        return JsonResponse(response_data)
    
class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'habits/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habits = Habit.objects.filter(user=self.request.user)
        context['habits'] = habits
        return context
class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    fields = ['name', 'description', 'periodicity']
    success_url = reverse_lazy('habits:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class HabitDetailView(LoginRequiredMixin, DetailView):
    model = Habit
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habit = self.get_object()
        
        # Add statistics to context
        context.update({
            'current_streak': habit.get_streak(),
            'completion_rate': habit.get_completion_rate(),
            'completions': habit.completions.order_by('-completed_at')[:10],  # Last 10 completions
        })
        
        return context
""" Analytics """

class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'habits/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habits = self.request.user.habits.all()

        # Calculate overall statistics
        context.update({
            'total_habits': habits.count(),
            'total_completions': sum(h.completions.count() for h in habits),
            'success_rate': self.calculate_overall_success_rate(habits),
            'longest_streak': max((h.get_streak() for h in habits), default=0),
            'habits': habits,
        })

        # Prepare chart data
        context.update({
            'completion_data': self.get_completion_trend_data(habits),
            'day_success_data': self.get_day_success_data(habits),
        })

        return context

    def calculate_overall_success_rate(self, habits):
        if not habits:
            return 0
        
        total_required = 0
        total_completed = 0
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        for habit in habits:
            if habit.periodicity == 'daily':
                total_required += 30
            else:  # weekly
                total_required += 4
            
            total_completed += habit.completions.filter(
                completed_at__gte=thirty_days_ago
            ).count()
        
        return round((total_completed / total_required * 100) if total_required > 0 else 0, 1)

    def get_completion_trend_data(self, habits):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Get daily completion counts
        completions = {}
        for habit in habits:
            for completion in habit.completions.filter(completed_at__gte=thirty_days_ago):
                date = completion.completed_at.date().isoformat()
                completions[date] = completions.get(date, 0) + 1

        # Generate all dates for the last 30 days
        dates = [(timezone.now().date() - timedelta(days=x)) for x in range(30)]
        dates.reverse()

        return {
            'labels': [date.strftime('%Y-%m-%d') for date in dates],
            'values': [completions.get(date.isoformat(), 0) for date in dates]
        }

    def get_day_success_data(self, habits):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        success_rates = []
        
        for day_number in range(7):
            completions = sum(
                habit.completions.filter(completed_at__week_day=day_number + 1).count()
                for habit in habits
            )
            total_weeks = 4  # Consider last 4 weeks
            expected = sum(1 for habit in habits if habit.periodicity == 'daily') * total_weeks
            success_rate = (completions / expected * 100) if expected > 0 else 0
            success_rates.append(round(success_rate, 1))

        return {
            'labels': days,
            'values': success_rates
        }

    def get_best_and_struggling_habits(self, habits):
        """Identify best performing and struggling habits"""
        habit_stats = []
        for habit in habits:
            completion_rate = habit.get_completion_rate()
            habit_stats.append({
                'habit': habit,
                'completion_rate': completion_rate,
                'streak': habit.get_streak(),
            })
        
        # Sort by completion rate
        habit_stats.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        return {
            'best_performing': habit_stats[:3] if habit_stats else [],
            'struggling': [h for h in habit_stats if h['completion_rate'] < 50][:3]
        }
class HabitCompletionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        habit = get_object_or_404(Habit, pk=pk, user=request.user)
        
        # Create completion
        completion = HabitCompletion.objects.create(
            habit=habit,
            completed_at=timezone.now()
        )
        
        # Get updated streak
        current_streak = habit.get_streak()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Habit completed successfully!',
            'streak': current_streak,
            'next_due': habit.get_next_due_date()
        })
class HabitTrackerView(LoginRequiredMixin, TemplateView):
    template_name = 'habits/habit_tracker.html'
def get_success_url(self):
    return reverse_lazy('habits:dashboard')
@login_required
def manual_complete_habit(request, habit_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        
        completion_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        HabitCompletion.objects.create(
            habit=habit,
            completed_at=completion_date
        )
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})
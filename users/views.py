from django.views.generic import UpdateView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordChangeView
from .models import UserProfile
from .forms import UserProfileForm, NotificationSettingsForm, PasswordChangeForm
from django.http import HttpResponse
import csv, json
from django.views.generic import FormView
from .forms import ExportDataForm
from datetime import datetime, timedelta, time
from django.utils import timezone
from habits.models import Habit, HabitCompletion
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import io
import pytz



class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'timezone': 'UTC',
                'theme': 'system',
                'notification_preferences': {
                    'email_notifications': True,
                    'daily_reminders': False,
                    'weekly_summary': True
                }
            }
        )
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add notification settings to context
        context['notification_settings'] = self.object.get_notification_settings()
        
        # Add user stats
        context.update({
            'active_habits': self.request.user.habits.count(),
            'completed_today': self.request.user.habits.filter(
                completions__completed_at__date=timezone.now().date()
            ).distinct().count(),
            'longest_streak': max(
                (habit.get_streak() for habit in self.request.user.habits.all()),
                default=0
            )
        })
        
        return context

    def form_valid(self, form):
        # Save the user's basic info
        user = self.request.user
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.email = form.cleaned_data.get('email', '')
        user.save()

        # Handle notification preferences
        notification_settings = {
            'email_notifications': form.cleaned_data.get('email_notifications', False),
            'daily_reminders': form.cleaned_data.get('daily_reminders', False),
            'weekly_summary': form.cleaned_data.get('weekly_report', False)
        }

        # Update profile instance
        profile = form.instance
        profile.user = user
        profile.notification_preferences = notification_settings
        
        # Handle daily reminder time
        if not notification_settings['daily_reminders']:
            profile.daily_reminder_time = None

        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notification_settings'] = self.object.get_notification_settings()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)   

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error changing password!')
        return super().form_invalid(form)

class NotificationPreferencesView(LoginRequiredMixin, UpdateView):
    """Update notification preferences"""
    model = UserProfile
    template_name = 'users/notification_preferences.html'
    fields = ['notification_preferences', 'daily_reminder_time', 'weekly_report']
    success_url = reverse_lazy('users:settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Notification preferences updated!')
        return super().form_valid(form)

class ExportDataView(LoginRequiredMixin, FormView):
    template_name = 'users/export_data.html'
    form_class = ExportDataForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        file_format = form.cleaned_data['format']
        data_type = form.cleaned_data['data_type']
        date_range = form.cleaned_data['date_range']

        # Get date range
        end_date = timezone.now()
        if date_range == 'year':
            start_date = end_date - timedelta(days=365)
        elif date_range == 'month':
            start_date = end_date - timedelta(days=30)
        elif date_range == 'week':
            start_date = end_date - timedelta(days=7)
        else:
            start_date = None

        # Get export data
        data = self.get_export_data(data_type, start_date)

        # Create response
        if file_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{data_type}_{date_range}.csv"'
            writer = csv.writer(response)
            
            # Write headers and data
            if data_type == 'habits':
                writer.writerow(['Name', 'Description', 'Periodicity', 'Created', 'Completions'])
                for habit in data:
                    writer.writerow([
                        habit.name,
                        habit.description,
                        habit.get_periodicity_display(),
                        habit.created_at,
                        habit.completions.count()
                    ])
            
        else:  # JSON
            response = HttpResponse(json.dumps(data, default=str), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{data_type}_{date_range}.json"'

        return response

    def get_export_data(self, data_type, start_date=None):
        user = self.request.user
        queryset = None

        if data_type == 'habits':
            queryset = Habit.objects.filter(user=user)
        elif data_type == 'completions':
            queryset = HabitCompletion.objects.filter(habit__user=user)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        return queryset

class DeleteAccountView(LoginRequiredMixin, TemplateView):
    """Delete user account"""
    template_name = 'users/delete_account.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        # Log the user out and delete their account
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')

class RegisterView(CreateView):
    """Handle user registration"""
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response
def get_unread_notifications(self):
    return self.user.notifications.filter(is_read=False)

def mark_notifications_read(self):
    self.user.notifications.filter(is_read=False).update(is_read=True)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

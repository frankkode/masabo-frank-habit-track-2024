from django import forms
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from datetime import time
import pytz




User = get_user_model()

class UserProfileForm(forms.ModelForm):
    """Combined form for user profile and notification settings"""
    
    # User fields
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    # Profile fields
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden'
        })
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        }), 
        required=False
    )
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    theme = forms.ChoiceField(
        choices=UserProfile.THEME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    # Notification preferences
    email_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'
        })
    )
    daily_reminders = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'
        })
    )
    weekly_report = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'
        })
    )
    daily_reminder_time = forms.TimeField(
        required=False,
        input_formats=['%H:%M', '%I:%M %p', '%I:%M%p'],
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        }),
        help_text="Set your daily reminder time"
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'avatar', 'bio',
            'timezone', 'theme', 'email_notifications',
            'daily_reminders', 'weekly_report', 'daily_reminder_time'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            # Set initial values from user model
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            
            # Set initial values from notification settings
            settings = self.instance.get_notification_settings()
            self.fields['email_notifications'].initial = settings.get('email_notifications')
            self.fields['daily_reminders'].initial = settings.get('daily_reminders')
            self.fields['weekly_report'].initial = settings.get('weekly_summary')
            
            # Set initial time value
            if self.instance.daily_reminder_time:
                self.fields['daily_reminder_time'].initial = self.instance.daily_reminder_time

    def clean_daily_reminder_time(self):
        """Clean and validate daily reminder time"""
        daily_reminders = self.cleaned_data.get('daily_reminders')
        reminder_time = self.cleaned_data.get('daily_reminder_time')

        if daily_reminders:
            return reminder_time if reminder_time else time(9, 0)
        return None

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update user information
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

        # Update notification settings
        profile.update_notification_settings({
            'email_notifications': self.cleaned_data['email_notifications'],
            'daily_reminders': self.cleaned_data['daily_reminders'],
            'weekly_summary': self.cleaned_data['weekly_report']
        })

        # Handle daily reminder time
        if self.cleaned_data['daily_reminders']:
            profile.daily_reminder_time = self.cleaned_data.get('daily_reminder_time') or time(9, 0)
        else:
            profile.daily_reminder_time = None

        if commit:
            profile.save()
        return profile


class PasswordChangeForm(BasePasswordChangeForm):
    """Custom password change form"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            })
        
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'


class DeleteAccountForm(forms.Form):
    """Form for account deletion confirmation"""
    confirm_email = forms.EmailField(
        help_text="Enter your email to confirm account deletion",
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_confirm_email(self):
        email = self.cleaned_data.get('confirm_email')
        if email != self.user.email:
            raise forms.ValidationError("Email doesn't match your account email.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password


class ExportDataForm(forms.Form):
    """Form for exporting user data"""
    EXPORT_CHOICES = [
        ('all', 'All Data'),
        ('habits', 'Habits Only'),
        ('completions', 'Completions Only'),
        ('analytics', 'Analytics Only')
    ]
    
    data_type = forms.ChoiceField(
        choices=EXPORT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500'
        })
    )
    format = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('json', 'JSON')],
        widget=forms.RadioSelect(attrs={
            'class': 'h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500'
        })
    )
    date_range = forms.ChoiceField(
        choices=[
            ('all', 'All Time'),
            ('year', 'Past Year'),
            ('month', 'Past Month'),
            ('week', 'Past Week')
        ],
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
class NotificationSettingsForm(forms.Form):
    """Form for updating notification settings"""
    email_notifications = forms.BooleanField(required=False)
    push_notifications = forms.BooleanField(required=False)
    streak_milestones = forms.BooleanField(required=False)
    daily_reminders = forms.BooleanField(required=False)
    weekly_summary = forms.BooleanField(required=False)
    daily_reminder_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                'placeholder': 'HH:MM'
            }
        )
    )

    class Meta:
        widgets = {
            'daily_reminder_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-input rounded-md shadow-sm mt-1 block w-full'
                }
            )
        }

class PasswordChangeForm(BasePasswordChangeForm):
    """Custom password change form"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class DeleteAccountForm(forms.Form):
    """Form for account deletion confirmation"""
    confirm_email = forms.EmailField(help_text="Enter your email to confirm account deletion")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_confirm_email(self):
        email = self.cleaned_data.get('confirm_email')
        if email != self.user.email:
            raise forms.ValidationError("Email doesn't match your account email.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password

class ExportDataForm(forms.Form):
    """Form for exporting user data"""
    EXPORT_CHOICES = [
        ('all', 'All Data'),
        ('habits', 'Habits Only'),
        ('completions', 'Completions Only'),
        ('analytics', 'Analytics Only')
    ]
    
    data_type = forms.ChoiceField(
        choices=EXPORT_CHOICES,
        widget=forms.RadioSelect
    )
    format = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'), 
            ('json', 'JSON')
        ],
        widget=forms.RadioSelect
    )
    date_range = forms.ChoiceField(
        choices=[
            ('all', 'All Time'),
            ('year', 'Past Year'),
            ('month', 'Past Month'),
            ('week', 'Past Week')
        ],
        widget=forms.Select(attrs={'class': 'form-select rounded-lg'})
    )
class PasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap/Tailwind classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            })
            
        # Customize labels and help texts
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'
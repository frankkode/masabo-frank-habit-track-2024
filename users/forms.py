from django import forms
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from django.contrib.auth import get_user_model
from .models import UserProfile
import pytz


User = get_user_model()
# templatetags/form_tags.py

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    avatar = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control rounded-lg'
        }), 
        required=False
    )
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        widget=forms.Select(attrs={'class': 'form-select rounded-lg'})
    )
    theme = forms.ChoiceField(
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('system', 'System')
        ],
        widget=forms.Select(attrs={'class': 'form-select rounded-lg'})
    )
    email_notifications = forms.BooleanField(required=False)
    daily_reminders = forms.BooleanField(required=False)
    weekly_report = forms.BooleanField(required=False)
    daily_reminder_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control rounded-lg'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'avatar', 'bio',
            'timezone', 'theme', 'email_notifications', 'daily_reminders',
            'weekly_report', 'daily_reminder_time'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            settings = self.instance.get_notification_settings()
            self.fields['email_notifications'].initial = settings.get('email_notifications')
            self.fields['daily_reminders'].initial = settings.get('daily_reminders')
            self.fields['weekly_report'].initial = settings.get('weekly_summary')

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update User model fields
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
            profile.save()
        return profile
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
    file_format = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('json', 'JSON')],
        widget=forms.RadioSelect
    )
    date_range = forms.ChoiceField(
        choices=[
            ('all', 'All Time'),
            ('year', 'Past Year'),
            ('month', 'Past Month'),
            ('week', 'Past Week')
        ],
        widget=forms.Select
    )

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
    data_type = forms.ChoiceField(choices=[
        ('habits', 'Habits'),
        ('completions', 'Completions'),
    ])
    format = forms.ChoiceField(choices=[
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ])
    date_range = forms.ChoiceField(choices=[
        ('all', 'All Time'),
        ('year', 'Last Year'),
        ('month', 'Last Month'),
        ('week', 'Last Week'),
    ])

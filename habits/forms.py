from django import forms
from .models import Habit, HabitCompletion

class HabitForm(forms.ModelForm):
    """Form for creating and updating habits"""
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False
    )
    
    class Meta:
        model = Habit
        fields = ['name', 'description', 'periodicity', 'start_date', 'color']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class HabitCompletionForm(forms.ModelForm):
    """Form for recording habit completions"""
    MOOD_CHOICES = [
        ('great', '😊 Great'),
        ('good', '🙂 Good'),
        ('neutral', '😐 Neutral'),
        ('bad', '🙁 Bad'),
        ('terrible', '😫 Terrible')
    ]
    
    mood = forms.ChoiceField(choices=MOOD_CHOICES, required=False)
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )
    
    class Meta:
        model = HabitCompletion
        fields = ['note', 'mood']

class HabitFilterForm(forms.Form):
    """Form for filtering habits on dashboard"""
    PERIOD_CHOICES = [
        ('all', 'All Time'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month')
    ]
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    periodicity = forms.ChoiceField(
        choices=[('all', 'All')] + Habit.PERIODICITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    completed = forms.BooleanField(required=False)

class BulkHabitCompletionForm(forms.Form):
    """Form for completing multiple habits at once"""
    habits = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['habits'].queryset = Habit.objects.filter(user=user)
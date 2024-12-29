import pytest
from django.utils import timezone
from habits.forms import HabitForm

class TestHabitForm:
    def test_valid_form(self):
        form = HabitForm(data={
            'name': 'Test Habit',
            'periodicity': 'daily',
            'target_completions': 1,
            'description': 'Test description',
            'start_date': timezone.now().date(),
            'color': '#3B82F6'
        })
        assert form.is_valid(), form.errors
from django.utils import timezone
from datetime import timedelta, datetime
from typing import List, Dict, Optional

class StreakCalculator:
    """
    A utility class for calculating habit streaks with improved accuracy
    """
    
    def __init__(self, habit):
        self.habit = habit
        self.completions = list(
            habit.completions.all()
            .order_by('completed_at')
            .values_list('completed_at', flat=True)
        )

    def calculate_longest_streak(self) -> int:
        """
        Calculate the longest streak ever achieved
        Returns the number of days in the longest streak
        """
        if not self.completions:
            return 0

        streaks = []
        current_streak = 1
        longest_streak = 1

        # Convert to dates for easier comparison
        completion_dates = [c.date() for c in self.completions]
        completion_dates.sort()

        for i in range(1, len(completion_dates)):
            current_date = completion_dates[i]
            prev_date = completion_dates[i-1]
            
            # Check if dates are consecutive based on periodicity
            if self._are_dates_consecutive(prev_date, current_date):
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1

            longest_streak = max(longest_streak, current_streak)

        streaks.append(current_streak)  # Add the last streak
        return max(streaks)

    def calculate_current_streak(self) -> int:
        """
        Calculate the current active streak
        Returns the number of days in the current streak
        """
        if not self.completions:
            return 0

        today = timezone.now().date()
        completion_dates = [c.date() for c in self.completions]
        completion_dates.sort(reverse=True)
        
        # Check if the habit is still active (completed within the allowed interval)
        if not self._is_streak_active(completion_dates[0]):
            return 0

        current_streak = 1
        for i in range(len(completion_dates) - 1):
            current_date = completion_dates[i]
            next_date = completion_dates[i + 1]
            
            if self._are_dates_consecutive(next_date, current_date):
                current_streak += 1
            else:
                break

        return current_streak

    def _are_dates_consecutive(self, date1: datetime.date, date2: datetime.date) -> bool:
        """
        Check if two dates are consecutive based on habit periodicity
        """
        if self.habit.periodicity == 'daily':
            return (date2 - date1).days == 1
        elif self.habit.periodicity == 'weekly':
            days_diff = (date2 - date1).days
            return 6 <= days_diff <= 8  # Allow some flexibility for weekly habits
        return False

    def _is_streak_active(self, last_completion_date: datetime.date) -> bool:
        """
        Check if the streak is still active based on the last completion date
        """
        today = timezone.now().date()
        days_since_last = (today - last_completion_date).days

        if self.habit.periodicity == 'daily':
            return days_since_last <= 1
        elif self.habit.periodicity == 'weekly':
            return days_since_last <= 7
        return False

    def get_streak_details(self) -> Dict:
        """
        Get detailed streak information
        """
        current_streak = self.calculate_current_streak()
        longest_streak = self.calculate_longest_streak()
        
        last_completion = max(self.completions).date() if self.completions else None
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_completion': last_completion,
            'is_active': self._is_streak_active(last_completion) if last_completion else False,
            'total_completions': len(self.completions)
        }

    def get_streak_milestones(self) -> List[int]:
        """
        Get all streak milestones achieved (7, 30, 100 days, etc.)
        """
        longest = self.calculate_longest_streak()
        milestones = [7, 30, 100]
        return [m for m in milestones if longest >= m]


def calculate_habit_streaks(habit):
    calculator = StreakCalculator(habit)
    return calculator.get_streak_details()

def get_longest_streak(habits):
    """Calculate longest streak across all habits"""
    longest_overall = 0
    streak_details = {}
    
    for habit in habits:
        calculator = StreakCalculator(habit)
        details = calculator.get_streak_details()
        streak_details[habit.id] = details
        longest_overall = max(longest_overall, details['longest_streak'])
    
    return longest_overall, streak_details
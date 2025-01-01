from rest_framework import serializers
from .models import Habit, HabitCompletion

class HabitSerializer(serializers.ModelSerializer):
    completion_rate = serializers.FloatField(read_only=True)
    streak = serializers.IntegerField(read_only=True)

    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'periodicity', 
                 'target_completions', 'completion_rate', 'streak']

class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCompletion
        fields = ['id', 'habit', 'completed_at', 'note']
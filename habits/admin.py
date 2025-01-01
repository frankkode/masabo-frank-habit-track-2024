from django.contrib import admin
from .models import Habit, HabitCompletion, Notification

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'periodicity', 'created_at', 'get_current_streak', 'get_completion_percentage']
    list_filter = ['periodicity', 'created_at', 'user']
    search_fields = ['name', 'description', 'user__username']
    ordering = ['-created_at']

    def get_current_streak(self, obj):
        return f"{obj.get_current_streak()} days"
    get_current_streak.short_description = 'Current Streak'

    def get_completion_percentage(self, obj):
        return f"{obj.get_completion_percentage()}%"
    get_completion_percentage.short_description = 'Completion Rate'

@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ['habit', 'completed_at', 'note', 'mood']
    list_filter = ['completed_at', 'habit']
    search_fields = ['habit__name', 'note']
    ordering = ['-completed_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'habit', 'type', 'created_at', 'read']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['user__username', 'habit__name', 'message']
    ordering = ['-created_at']
from django.contrib import admin
from .models import Habit, HabitCompletion, Notification
from django.contrib.admin import AdminSite

AdminSite.site_header = 'Habit Tracker Administration'
AdminSite.site_title = 'Habit Tracker Admin'
AdminSite.index_title = 'Habit Tracker Management'

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'periodicity', 'created_at', 'get_streak', 'get_completion_rate')
    list_filter = ('periodicity', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    date_hierarchy = 'created_at'
    
    def get_completion_rate(self, obj):
        return f"{obj.get_completion_rate():.1f}%"
    get_completion_rate.short_description = 'Completion Rate'

@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'completed_at', 'mood')
    list_filter = ('completed_at', 'mood', 'habit__periodicity')
    search_fields = ('habit__name', 'note')
    date_hierarchy = 'completed_at'
    raw_id_fields = ('habit',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'habit', 'type', 'created_at', 'read')
    list_filter = ('type', 'read', 'created_at')
    search_fields = ('message', 'user__username', 'habit__name')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'habit')
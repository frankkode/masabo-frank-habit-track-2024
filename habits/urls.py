from django.urls import path
from . import views

app_name = 'habits'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    # Habit CRUD
    path('habit/create/', views.HabitCreateView.as_view(), name='habit_create'),
    path('habit/<int:pk>/', views.HabitDetailView.as_view(), name='habit_detail'),
    path('habit/<int:pk>/edit/', views.HabitUpdateView.as_view(), name='habit_update'),
    path('habit/<int:pk>/delete/', views.HabitDeleteView.as_view(), name='habit_delete'),
    # Habit Completion
    path('habit/<int:pk>/complete/', views.HabitCompletionView.as_view(), name='habit_complete'),
    path('habit/bulk-complete/', views.BulkHabitCompletionView.as_view(), name='habit_bulk_complete'),
    
    # Analytics
    path('analytics/habit/<int:pk>/', views.HabitAnalyticsView.as_view(), name='habit_analytics'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),  
    path('bulk-complete/', 
         views.BulkHabitCompletionView.as_view(), 
         name='bulk-complete'),
    path('tracker/', views.HabitTrackerView.as_view(), name='habit_tracker'),
    path('habit/<int:habit_id>/manual-complete/', views.manual_complete_habit, name='manual_complete_habit'),
    
]
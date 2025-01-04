from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from users.views import RegisterView

app_name = 'users'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('notifications/', views.NotificationPreferencesView.as_view(), name='notification_preferences'),
    path('export/', views.ExportDataView.as_view(), name='export_data'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password/', views.CustomPasswordChangeView.as_view(), name='password_change'), 
    
]
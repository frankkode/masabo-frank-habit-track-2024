# Generated by Django 5.1.4 on 2024-12-21 10:48

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('periodicity', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('color', models.CharField(default='#3B82F6', max_length=7)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='habits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='HabitCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('note', models.TextField(blank=True)),
                ('mood', models.CharField(blank=True, max_length=20)),
                ('habit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completions', to='habits.habit')),
            ],
            options={
                'ordering': ['-completed_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('reminder', 'Reminder'), ('streak', 'Streak Achievement'), ('break', 'Streak Break'), ('milestone', 'Milestone')], max_length=20)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('habit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='habits.habit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

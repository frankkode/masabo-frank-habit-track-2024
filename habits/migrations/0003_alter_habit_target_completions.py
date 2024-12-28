# Generated by Django 5.1.4 on 2024-12-26 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0002_habit_target_completions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="habit",
            name="target_completions",
            field=models.PositiveIntegerField(
                help_text="Number of times to complete this habit"
            ),
        ),
    ]

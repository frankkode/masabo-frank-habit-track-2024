# Generated by Django 5.1.4 on 2024-12-28 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_userprofile_options_alter_userprofile_avatar_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="daily_reminder",
            field=models.TimeField(blank=True, null=True),
        ),
    ]

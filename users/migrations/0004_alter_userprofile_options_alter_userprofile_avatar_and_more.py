# Generated by Django 5.1.4 on 2024-12-27 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_notification"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userprofile",
            options={
                "verbose_name": "User Profile",
                "verbose_name_plural": "User Profiles",
            },
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="avatars/default.png",
                null=True,
                upload_to="avatars/",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="notification_preferences",
            field=models.JSONField(
                default=dict, help_text="User notification preferences"
            ),
        ),
    ]

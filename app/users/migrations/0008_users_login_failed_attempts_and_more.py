# Generated by Django 5.1.3 on 2024-12-07 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_users_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='login_failed_attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='users',
            name='temporary_disabled_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
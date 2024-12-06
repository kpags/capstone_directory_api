# Generated by Django 5.1.3 on 2024-11-23 12:05

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0004_users_student_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.TextField()),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifier', to='users.users')),
                ('to_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.capstonegroups')),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notified_to', to='users.users')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationRead',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.users')),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.notifications')),
            ],
        ),
    ]

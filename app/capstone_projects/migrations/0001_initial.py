# Generated by Django 5.1.3 on 2024-11-21 12:25

import django.contrib.postgres.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_remove_users_advisory_group_technicaladvisorgroups'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapstoneProjects',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.TextField()),
                ('ip_registration', models.TextField(blank=True, null=True)),
                ('acm_paper', models.TextField(blank=True, null=True)),
                ('full_document', models.TextField(blank=True, null=True)),
                ('pubmat', models.TextField(blank=True, null=True)),
                ('approval_form', models.TextField(blank=True, null=True)),
                ('source_code', models.TextField(blank=True, null=True)),
                ('members', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, null=True, size=None)),
                ('keywords', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, null=True, size=None)),
                ('is_best_project', models.BooleanField(default=False)),
                ('date_published', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('capstone_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='users.capstonegroups')),
            ],
        ),
    ]
# Generated by Django 5.1.3 on 2024-11-21 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_users_advisory_group_technicaladvisorgroups'),
    ]

    operations = [
        migrations.AddField(
            model_name='capstonegroups',
            name='course',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='capstonegroups',
            name='specialization',
            field=models.CharField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-07 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstone_projects', '0004_alter_capstoneprojects_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='capstoneprojects',
            name='course',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='capstoneprojects',
            name='specialization',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
# Generated by Django 5.0.3 on 2024-04-18 19:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emp', '0018_meeting'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='progress_percentage',
            field=models.IntegerField(default=0, help_text='Progress percentage for tasks that are "In Progress"', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='taskassignee',
            name='progress',
            field=models.IntegerField(default=0, help_text='Specific progress for tasks that are "In Progress"', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='taskassignee',
            name='status',
            field=models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Not Started', max_length=50),
        ),
    ]
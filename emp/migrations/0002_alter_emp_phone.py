# Generated by Django 5.0.3 on 2024-03-29 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emp',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]

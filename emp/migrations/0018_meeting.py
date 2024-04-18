# Generated by Django 4.1 on 2024-04-18 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emp', '0017_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('participants', models.ManyToManyField(to='emp.emp')),
            ],
        ),
    ]

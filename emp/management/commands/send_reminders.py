from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from emp.models import Task  # Make sure to adjust the import to your project's structure

class Command(BaseCommand):
    help = 'Sends reminders for tasks nearing their deadlines.'

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_times = [24, 48, 72]  # in hours

        for hours in reminder_times:
            check_time = now + timedelta(hours=hours)
            tasks = Task.objects.filter(deadline__range=(now, check_time))
            if tasks.exists():
                for task in tasks:
                    recipients = [assignee.emp.email for assignee in task.taskassignee_set.all()]  # Assuming Task has related TaskAssignees with emp relation
                    email_body = (
                        "Dear Employees,\n\n"
                        f"Reminder: The task '{task.title}' is nearing its deadline on {task.deadline.strftime('%Y-%m-%d %H:%M')}."
                        "\n\nBest regards,\nEmployee Task Pro Team"
                    )
                    send_mail(
                        'Task Deadline Reminder',
                        email_body,
                        'employeetaskpro@outlook.com',  # From email
                        recipients,
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f'Reminder sent for task "{task.title}" with deadline at {task.deadline}'))

            else:
                self.stdout.write(self.style.WARNING(f'No tasks with deadlines within {hours} hours.'))

        self.stdout.write(self.style.SUCCESS('Finished sending reminders.'))

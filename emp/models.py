from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Emp(models.Model):
    firstname=models.CharField(max_length=200)
    fathername=models.CharField(max_length=200)
    lastname=models.CharField(max_length=200)
    gender = models.TextField(blank=True,null= True) 
    dob = models.DateField(blank=True,null= True) 
    emp_id=models.CharField(max_length=200)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    date_hired = models.DateField(default=timezone.now) 
    salary = models.FloatField(default=0) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    address = models.CharField(max_length=100, null=True)
    status=models.BooleanField(default=True)
    department=models.CharField(max_length=200, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.firstname + ' ' +self.fathername + ' '+self.lastname + ' '
    
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)  

    urgency = models.CharField(
        max_length=50, 
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], 
        default='Low'
    )
    status = models.CharField(
        max_length=50, 
        choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], 
        default='Not Started'
    )
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class TaskAssignee(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    emp = models.ForeignKey('Emp', on_delete=models.CASCADE)
    weight = models.IntegerField(help_text='Percentage of task responsibility')

    class Meta:
        unique_together = ('task', 'emp')

    def __str__(self):
        return f"{self.emp.firstname} - {self.task.title}: {self.weight}%"

class WhistleblowingCase(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Open', 'Open'),
        ('Pending', 'Pending'),
        ('Under Investigation', 'Under Investigation'),
        ('Closed', 'Closed')
    ]

    involved_employees = models.ManyToManyField(User, related_name='whistleblowing_cases')
    description = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_cases')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Submitted')
    attachment = models.FileField(upload_to='whistleblowing_attachments/', null=True, blank=True)
    decision_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Case #{self.id} on {self.date_time.strftime('%Y-%m-%d')}"

class CaseConversation(models.Model):
    case = models.ForeignKey(WhistleblowingCase, related_name='conversations', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation for Case #{self.case.id} by {self.sender.username}"
    
class Feedback(models.Model):
    task = models.ForeignKey(Task, related_name='feedbacks', on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.created_by.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    

class Sprint(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tasks = models.ManyToManyField(Task)
    employees = models.ManyToManyField(Emp)

    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%Y-%m-%d')} - {self.end_date.strftime('%Y-%m-%d')})"
    
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"
    
class Meeting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Emp)  # Assuming Emp is your Employee model

    def __str__(self):
        return self.title
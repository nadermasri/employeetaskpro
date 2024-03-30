from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils import timezone


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
    
    def __str__(self):
        return self.firstname + ' ' +self.fathername + ' '+self.lastname + ' '
    
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(Emp, on_delete=models.CASCADE, related_name='tasks')
    deadline = models.DateTimeField(null=True, blank=True)
    urgency = models.CharField(max_length=50, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low')
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Pending')
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
from django.urls import path
from .views import *


app_name = 'emp'
urlpatterns = [
    path('update-task-status/<int:task_id>/', update_task_status, name='update_task_status'),
    path("home/", emp_home, name='emp_home'),
    path('login/', custom_login, name='custom_login'),
    path("add-emp/", add_emp, name='add_emp'),
    path("delete-emp/<int:emp_id>", delete_emp, name='delete_emp'),
    path("update-emp/<int:emp_id>", update_emp, name='update_emp'),
    path("do-update-emp/<int:emp_id>", do_update_emp, name='do_update_emp'),
    path("assign-task/", assign_task, name='assign_task'),
    path("my-tasks/", my_tasks, name='my_tasks'),
    path('hr-tasks/', hr_task_overview, name='hr_task_overview'),
    path('emp-dashboard/', emp_dashboard, name='emp_dashboard'),
]




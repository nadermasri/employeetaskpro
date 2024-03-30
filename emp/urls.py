from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path("home/",emp_home),
    path("add-emp/",add_emp),
    path("delete-emp/<int:emp_id>",delete_emp),
    path("update-emp/<int:emp_id>",update_emp),
    path("do-update-emp/<int:emp_id>",do_update_emp),
    path("assign-task/", assign_task, name='assign_task'),
    path("my-tasks/", my_tasks, name='my_tasks'),
]

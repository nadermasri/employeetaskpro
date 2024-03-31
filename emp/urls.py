from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'emp'
urlpatterns = [
    path("home/", emp_home, name='emp_home'),
    path('login/', custom_login, name='custom_login'),
    path("add-emp/", add_emp, name='add_emp'),
    path("delete-emp/<int:emp_id>", delete_emp, name='delete_emp'),
    path("update-emp/<int:emp_id>", update_emp, name='update_emp'),
    path("do-update-emp/<int:emp_id>", do_update_emp, name='do_update_emp'),
    path("assign-task/", assign_task, name='assign_task'),
    path("my-tasks/", my_tasks, name='my_tasks'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

]




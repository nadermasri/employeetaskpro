"""myapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *
import emp.views as fun
from .views import custom_login
from django.contrib.auth import views as auth_views
# from django.contrib.auth.views import LogoutView
from emp.views import add_sprint
from emp.views import add_meeting
from emp.views import home_view
# from emp import views



urlpatterns = [
    path('emp/', include('emp.urls', namespace='emp')),
    path('login/', custom_login, name='custom_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='emp:home_view'), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),  # make sure that your project's URL configuration includes Django's authentication views. If you haven't already, add the following line to your urls.py file in the main project directory 
    path('admin/', admin.site.urls),
    path("",fun.home_view),
    path("index/",fun.emp_home),
    path('add-sprint/', add_sprint, name='add_sprint'),
    path('add-meeting/', add_meeting, name='add_meeting')
]

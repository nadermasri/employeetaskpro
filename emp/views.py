from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Emp, Task
from .forms import TaskAssignForm
from django.utils import timezone


def emp_home(request):
    emps=Emp.objects.all()
    return render(request,"emp/home.html",{'emps':emps})


def add_emp(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        fathername = request.POST.get("fathername")
        lastname = request.POST.get("lastname")
        gender = request.POST.get("gender", "")
        dob = request.POST.get("dob", None)
        emp_id = request.POST.get("emp_id")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        date_hired = request.POST.get("date_hired", timezone.now().date())
        salary = request.POST.get("salary", 0)
        address = request.POST.get("address")
        status = request.POST.get("status", True)
        department = request.POST.get("department")

        e = Emp(firstname=firstname, fathername=fathername, lastname=lastname,
                gender=gender, dob=dob, emp_id=emp_id, phone=phone, email=email,
                date_hired=date_hired, salary=salary, address=address, status=status,
                department=department, date_added=timezone.now())
        e.save()
        return redirect("/emp/home/")
    return render(request, "emp/add_emp.html", {})

def delete_emp(request,emp_id):
    emp=Emp.objects.get(pk=emp_id)
    emp.delete()
    return redirect("/emp/home/")

def update_emp(request,emp_id):
    emp=Emp.objects.get(pk=emp_id)
    print("Yes Bhai")
    return render(request,"emp/update_emp.html",{
        'emp':emp
    })

def do_update_emp(request, emp_id):
    if request.method == "POST":
        emp = Emp.objects.get(pk=emp_id)

        emp.firstname = request.POST.get("firstname", emp.firstname)
        emp.fathername = request.POST.get("fathername", emp.fathername)
        emp.lastname = request.POST.get("lastname", emp.lastname)
        emp.gender = request.POST.get("gender", emp.gender)
        emp.dob = request.POST.get("dob", emp.dob)
        emp.emp_id = request.POST.get("emp_id", emp.emp_id)
        emp.phone = request.POST.get("phone", emp.phone)
        emp.email = request.POST.get("email", emp.email)
        emp.date_hired = request.POST.get("date_hired", emp.date_hired)
        emp.salary = request.POST.get("salary", emp.salary)
        emp.address = request.POST.get("address", emp.address)
        emp.status = request.POST.get("status", emp.status)
        emp.department = request.POST.get("department", emp.department)

        emp.save()
        return redirect("/emp/home/")

def assign_task(request):
    if request.method == 'POST':
        form = TaskAssignForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("/emp/home/")  # Use the 'emp:' namespace prefix
    else:
        form = TaskAssignForm()
    return render(request, 'emp/assign_task.html', {'form': form})

def my_tasks(request):
    tasks = Task.objects.filter(assignee=request.user.employee)  # Adjust according to your user-employee relationship
    return render(request, 'emp/my_tasks.html', {'tasks': tasks})


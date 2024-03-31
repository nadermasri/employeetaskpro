from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Emp, Task
from .forms import TaskAssignForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect
from .forms import TaskUpdateForm
from django.contrib import messages




@login_required
def emp_home(request):
    emps = Emp.objects.all()
    
    for emp in emps:
        tasks = Task.objects.filter(assignee=emp)
        completed_tasks = tasks.filter(status="Completed").count()
        total_tasks = tasks.count()
        progress = 100 * completed_tasks / total_tasks if total_tasks > 0 else 0
        emp.progress = progress  # Augment the Emp object with a progress attribute
    
    is_hr_or_manager = request.user.groups.filter(name__in=['HR', 'Manager']).exists()
    is_employee = request.user.groups.filter(name='Employee').exists()

    context = {
        'emps': emps,
        'is_hr_or_manager': is_hr_or_manager,
        'is_employee': is_employee,
    }

    return render(request, "emp/home.html", context)



@login_required
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

@login_required
def delete_emp(request,emp_id):
    emp=Emp.objects.get(pk=emp_id)
    emp.delete()
    return redirect("/emp/home/")

@login_required
def update_emp(request,emp_id):
    emp=Emp.objects.get(pk=emp_id)
    print("Yes Bhai")
    return render(request,"emp/update_emp.html",{
        'emp':emp
    })

@login_required
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
    
@login_required
def assign_task(request):
    if request.method == 'POST':
        form = TaskAssignForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("/emp/home/")  # Use the 'emp:' namespace prefix
    else:
        form = TaskAssignForm()
    return render(request, 'emp/assign_task.html', {'form': form})

# @login_required
# def my_tasks(request):
#     tasks = Task.objects.filter(assignee=request.user.employee)
#     return render(request, 'emp/my_tasks.html', {'tasks': tasks})


# @login_required
# def my_tasks(request):
#     try:
#         # Retrieve the logged-in user's employee profile
#         employee = request.user.employee
#         # Filter tasks by the employee
#         tasks = Task.objects.filter(assignee=employee)
#     except AttributeError:
#         # If the user doesn't have an employee profile, handle it appropriately
#         tasks = []
#         # You might want to redirect the user or show an error message
#         # For now, let's just print an error message
#         print("This user does not have an associated employee profile.")
    
#     return render(request, 'emp/my_tasks.html', {'tasks': tasks})
@login_required
def my_tasks(request):
    # Get all tasks along with the assignee and their progress
    all_tasks_with_progress = []
    all_tasks = Task.objects.select_related('assignee').all()  # Prefetch related assignee data

    for task in all_tasks:
        completed = 'Completed' if task.status == 'Completed' else 'In Progress'  # Or however you mark completion
        progress = '100%' if task.status == 'Completed' else 'In Progress'  # Assuming binary completion, not partial
        all_tasks_with_progress.append({
            'task': task,
            'assignee': task.assignee,
            'progress': progress,
            'status': completed
        })

    context = {'tasks_with_progress': all_tasks_with_progress}
    return render(request, 'emp/my_tasks.html', context)


# @login_required
def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('emp:emp_home')  # Note the 'emp:' namespace prefix
        else:
            # Return an 'invalid login' error message.
            return render(request, 'emp/login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'emp/login.html')

# @login_required
# def update_task_status(request, task_id):
#     if request.method == 'POST':
#         task = get_object_or_404(Task, pk=task_id, assignee=request.user)
#         form = TaskUpdateForm(request.POST, instance=task)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Task status updated.')
#             return redirect('my_tasks')
#         else:
#             messages.error(request, 'Error updating task status.')
#     else:
#         form = TaskUpdateForm()

#     return redirect('my_tasks')
# @login_required
# def update_task_status(request, task_id):
#     task = get_object_or_404(Task, pk=task_id, assignee=request.user.employee)  # This should reference the employee, not user directly
#     if request.method == 'POST':
#         form = TaskUpdateForm(request.POST, instance=task)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Task status updated.')
#             return redirect('emp:my_tasks')
#         else:
#             messages.error(request, 'Error updating task status.')
#     else:
#         form = TaskUpdateForm(instance=task)  # Pass the instance for GET request as well

#     # If you have a specific template for updating task status, render it
#     # return render(request, 'emp/update_task_status.html', {'form': form, 'task': task})

#     return redirect('emp:my_tasks')  # Redirect if not a POST request or if the form is not valid

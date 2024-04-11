from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Emp, Task, WhistleblowingCase, CaseConversation
from .forms import TaskAssignForm, WhistleblowingForm, ConversationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect
from .forms import TaskUpdateForm, WhistleblowingForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.http import HttpResponseRedirect


@login_required
def emp_home(request):
   
    if request.user.groups.filter(name='Employee').exists():
        return redirect('emp:my_tasks')

    emps = Emp.objects.all()
    for emp in emps:
        tasks = Task.objects.filter(assignees=emp)
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
        dob = request.POST.get("dob")
        dob_date = datetime.strptime(dob, "%Y-%m-%d") if dob else None  # Adjust date format as necessary
        form_data = {
            'firstname': request.POST.get("firstname", "").strip(),
            'fathername': request.POST.get("fathername", "").strip(),
            'lastname': request.POST.get("lastname", "").strip(),
            'gender': request.POST.get("gender", "").strip(),
            'dob': dob_date,
            'emp_id': request.POST.get("emp_id", "").strip(),
            'phone': request.POST.get("phone", "").strip(),
            'email': request.POST.get("email", "").strip(),
            'date_hired': request.POST.get("date_hired") or timezone.now().date(),
            'salary': request.POST.get("salary", 0),
            'address': request.POST.get("address", "").strip(),
            'status': 'status' in request.POST,
            'department': request.POST.get("department", "").strip(),
        }
        
        if len(form_data['phone']) < 8:
            messages.error(request, "Invalid phone number. Must be at least 8 characters.")
            return render(request, "emp/add_emp.html", {'form_data': form_data})

        if any(not value for key, value in form_data.items() if key != 'status'):  # Skip 'status' for this check
            messages.error(request, "Please fill out all required fields.")
            return render(request, "emp/add_emp.html", {'form_data': form_data})

        username_base = f"{form_data['firstname'][0]}{form_data['lastname']}".lower()
        plaintext_password = f"{form_data['phone'][-4:]}{dob_date.year if dob_date else ''}"

        unique = False
        counter = 1
        username = username_base
        while not unique:
            if User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            else:
                unique = True

        user = User.objects.create_user(  # Use create_user to handle password hashing
            username=username,
            password=plaintext_password,
            first_name=form_data['firstname'],
            last_name=form_data['lastname'],
            email=form_data['email'],
        )

        # Fetch the 'Employee' group
        employee_group = Group.objects.get(name='Employee')

        # Add the user to the 'Employee' group
        employee_group.user_set.add(user)


        e = Emp(**form_data, user=user, date_added=timezone.now())
        e.save()


       # After saving the employee record
        messages.success(request, "Employee added successfully.")
        return render(request, 'emp/employee_success.html', {'username': user.username, 'password':plaintext_password})
    else:
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
            task = form.save()
            # The call to form.save_m2m() is not needed as form.save() already commits the data
            return redirect("/emp/home/")  # Adjust the redirect as needed
    else:
        form = TaskAssignForm()
    return render(request, 'emp/assign_task.html', {'form': form})


@login_required
def my_tasks(request):
    user_emp = request.user.emp if hasattr(request.user, 'emp') else None

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        # Ensure the task belongs to the user among assignees
        task = get_object_or_404(Task, id=task_id, assignees=user_emp)
        task.status = new_status
        task.save()
        return HttpResponseRedirect(request.path_info)  # Use path_info to reload the same page

    tasks = Task.objects.filter(assignees=user_emp)  # Retrieve tasks where the user is one of the assignees
    status_to_progress = {
        'Not Started': 0,
        'In Progress': 50, 
        'Completed': 100
    }

    tasks_with_progress = [{
        'task': task,
        'assignees': task.assignees.all(),  # .all() is used to get all related Emp objects
        'progress': status_to_progress.get(task.status, 0),  
        'status': task.status
    } for task in tasks]

    context = {
        'tasks_with_progress': tasks_with_progress,
        'user_emp': user_emp,
    }
    return render(request, 'emp/my_tasks.html', context)


@login_required
def hr_task_overview(request):
    if not request.user.groups.filter(name='HR').exists():
        return redirect('emp:emp_home')  # Adjust the redirect as needed

    tasks = Task.objects.all().prefetch_related('assignees')
    context = {'tasks': tasks}
    return render(request, 'emp/hr_task_overview.html', context)


@login_required
def emp_dashboard(request):
    user_emp = request.user.emp if hasattr(request.user, 'emp') else None
    tasks = Task.objects.filter(assignees=user_emp)  # Adjusted to filter with assignees M2M field
    # Calculate task progress
    task_progress = {
        'Not Started': tasks.filter(status='Not Started').count(),
        'In Progress': tasks.filter(status='In Progress').count(),
        'Completed': tasks.filter(status='Completed').count(),
    }

    # Calculate percentages for each status
    total_tasks = sum(task_progress.values())
    task_progress_percentage = {status: (count / total_tasks * 100 if total_tasks > 0 else 0) for status, count in task_progress.items()}

    # Get completed tasks
    completed_tasks = tasks.filter(status='Completed')

    context = {
        'employee': user_emp,
        'task_progress': task_progress_percentage.items(),
        'completed_tasks': completed_tasks,
    }

    return render(request, 'emp/emp_dashboard.html', context)


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


    
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task status updated successfully.')
        else:
            messages.error(request, 'Error updating task status.')
    return redirect('emp:my_tasks')


@login_required
def submit_whistleblowing(request):
    if request.method == 'POST':
        form = WhistleblowingForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.submitted_by = request.user
            case.save()
            form.save_m2m()
            messages.success(request, 'Whistleblowing case submitted successfully.')
            return redirect('emp:whistleblowing_cases_overview')
    else:
        form = WhistleblowingForm()
    return render(request, 'emp/submit_whistleblowing.html', {'form': form})

@login_required
def whistleblowing_cases_overview(request):
    if request.user.groups.filter(name='HR').exists():
        cases = WhistleblowingCase.objects.all()  # HR can see all cases
    else:
        cases = WhistleblowingCase.objects.filter(submitted_by=request.user)  # Others see their own cases
    return render(request, 'emp/whistleblowing_cases_overview.html', {'cases': cases})

@login_required
def update_whistleblowing_case(request, case_id):
    case = get_object_or_404(WhistleblowingCase, id=case_id)
    if request.user.groups.filter(name='HR').exists() or case.submitted_by == request.user:
        if request.method == 'POST':
            case.status = request.POST.get('status')
            case.decision_description = request.POST.get('decision_description', '')
            case.save()
            messages.success(request, 'Whistleblowing case updated successfully.')
            return redirect('emp:whistleblowing_cases_overview')
        return render(request, 'emp/update_whistleblowing_case.html', {'case': case})
    else:
        return redirect('emp:whistleblowing_cases_overview')  # Redirect if not authorized

@login_required
def case_conversation(request, case_id):
    case = get_object_or_404(WhistleblowingCase, id=case_id)
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.case = case
            conversation.sender = request.user
            conversation.save()
            return redirect('emp:case_conversation', case_id=case_id)
    else:
        form = ConversationForm()
    conversations = case.conversations.all()
    return render(request, 'emp/case_conversation.html', {'form': form, 'conversations': conversations, 'case': case})

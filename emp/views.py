from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Emp, Task, WhistleblowingCase, CaseConversation, Feedback, TaskAssignee,Sprint, Message
from .forms import TaskAssignForm, WhistleblowingForm, ConversationForm, TaskForm,SprintForm, MessageForm
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
from django.db.models import Case, When
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.forms import formset_factory, modelformset_factory
from django.db.models import Count
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json



@login_required
def emp_home(request):
    # Get all employees
    emps = Emp.objects.all()

    # Iterate through each employee to calculate completed tasks count
    for emp in emps:
        tasks_assigned_to_employee = Task.objects.filter(taskassignee__emp=emp)
        completed_tasks_count = tasks_assigned_to_employee.filter(status='Completed').count()
        total_tasks_count = tasks_assigned_to_employee.count()
        progress_percentage = (completed_tasks_count / total_tasks_count) * 100 if total_tasks_count > 0 else 0
        emp.progress_percentage = progress_percentage

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
    emp = get_object_or_404(Emp, pk=emp_id)
    if request.method == "POST":
        emp.firstname = request.POST.get("firstname", emp.firstname)
        emp.fathername = request.POST.get("fathername", emp.fathername)
        emp.lastname = request.POST.get("lastname", emp.lastname)
        emp.gender = request.POST.get("gender", emp.gender)
        emp.dob = request.POST.get("dob", emp.dob)
        emp.emp_id = request.POST.get("emp_id", emp.emp_id)
        emp.phone = request.POST.get("phone", emp.phone)
        emp.email = request.POST.get("email", emp.email)
        emp.date_hired = request.POST.get("date_hired", emp.date_hired)
        emp.salary = float(request.POST.get("salary", emp.salary))
        emp.address = request.POST.get("address", emp.address)
        emp.department = request.POST.get("department", emp.department)
        emp.status = "emp_status" in request.POST  # Checkbox for active/inactive

        if emp.user:  # Check if there is an associated User object
            emp.user.is_active = emp.status
            emp.user.save()

        emp.save()
        messages.success(request, "Employee updated successfully.")
        return redirect('/emp/home/')
    else:
        return render(request, "emp/update_emp.html", {'emp': emp})


# Adding a new task
@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Task added successfully.")
            return redirect('emp:hr_task_overview')
    else:
        form = TaskForm()
    return render(request, 'emp/add_task.html', {'form': form})

@login_required
def assign_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    # Exclude already assigned and inactive employees
    unassigned_employees = Emp.objects.exclude(taskassignee__task=task).filter(status=True)
    existing_assignees = TaskAssignee.objects.filter(task=task)

    if request.method == 'POST':
        selected_emp_ids = request.POST.getlist('employees')
        weights = request.POST.getlist('weights')
        new_weights = sum(int(weight) for weight in weights)
        existing_weights_sum = existing_assignees.aggregate(Sum('weight'))['weight__sum'] or 0
        
        if new_weights + existing_weights_sum > 100:
            messages.error(request, "The sum of weights including existing assignees cannot exceed 100.")
            return redirect('emp:assign_task', task_id=task_id)
        
        for emp_id, weight in zip(selected_emp_ids, weights):
            employee = get_object_or_404(Emp, pk=emp_id)
            TaskAssignee.objects.create(task=task, emp=employee, weight=weight)

        messages.success(request, "Task assigned successfully.")
        return redirect('emp:hr_task_overview')

    context = {
        'task': task,
        'unassigned_employees': unassigned_employees,
        'existing_assignees': existing_assignees,
    }
    return render(request, 'emp/assign_task.html', context)

@login_required
def update_weights(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        # Collect all the new weights from the form
        weight_data = {
            assignee.id: request.POST.get(f"existing_weight_{assignee.id}", 0)
            for assignee in TaskAssignee.objects.filter(task=task)
        }
        
        # Convert to integers and sum them, treating empty strings as zeros
        total_weight = sum(int(weight) if weight.isdigit() else 0 for weight in weight_data.values())

        # Check if the total weight exceeds 100
        if total_weight > 100:
            messages.error(request, "The sum of weights cannot exceed 100.")
            return redirect('emp:assign_task',task_id=task_id)
        
        existing_assignees = TaskAssignee.objects.filter(task=task)
        for assignee in existing_assignees:
            weight = request.POST.get(f"existing_weight_{assignee.id}")
            if weight:
                assignee.weight = weight
                assignee.save()

        messages.success(request, "Weights updated successfully.")
    return redirect('emp:hr_task_overview')

@login_required
def my_tasks(request):
    user_emp = request.user.emp if hasattr(request.user, 'emp') else None
    sort = request.GET.get('sort', 'deadline')  # Default sorting by deadline

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        # Ensure the task belongs to the user among assignees
        task_assignee = get_object_or_404(TaskAssignee, task_id=task_id, emp=user_emp)
        task_assignee.task.status = new_status
        task_assignee.task.save()
        return HttpResponseRedirect(request.path_info)  # Use path_info to reload the same page

    # Retrieve task assignees associated with the user
    task_assignees = TaskAssignee.objects.filter(emp=user_emp).select_related('task')

    if sort == 'urgency':
        task_assignees = task_assignees.order_by(Case(
            When(task__urgency='High', then=1),
            When(task__urgency='Medium', then=2),
            When(task__urgency='Low', then=3),
            default=4
        ))
    else:  # Default sort by deadline
        task_assignees = task_assignees.order_by('task__deadline')

    status_to_progress = {
        'Not Started': 0,
        'In Progress': 50,
        'Completed': 100
    }

    tasks_with_progress = [{
        'task_assignee': task_assignee,
        'progress': status_to_progress.get(task_assignee.task.status, 0),
        'status': task_assignee.task.status
    } for task_assignee in task_assignees]

    context = {
        'tasks_with_progress': tasks_with_progress,
        'user_emp': user_emp,
        'current_sort': sort,
    }

    return render(request, 'emp/my_tasks.html', context)


@login_required
def hr_task_overview(request):
    if not request.user.groups.filter(name='HR').exists():
        return redirect('emp:emp_home')  # Adjust the redirect as needed

    tasks = Task.objects.all().prefetch_related('taskassignee_set__emp')
    context = {'tasks': tasks}
    return render(request, 'emp/hr_task_overview.html', context)


@login_required
def emp_dashboard(request):
    user_emp = request.user.emp if hasattr(request.user, 'emp') else None

    # Retrieve task assignees associated with the user
    task_assignees = TaskAssignee.objects.filter(emp=user_emp).select_related('task')

    # Calculate task progress
    task_progress = {
        'Not Started': task_assignees.filter(task__status='Not Started').count(),
        'In Progress': task_assignees.filter(task__status='In Progress').count(),
        'Completed': task_assignees.filter(task__status='Completed').count(),
    }

    # Calculate percentages for each status
    total_tasks = sum(task_progress.values())
    task_progress_percentage = {status: (count / total_tasks * 100 if total_tasks > 0 else 0) for status, count in task_progress.items()}

    # Get completed tasks
    completed_task_assignees = task_assignees.filter(task__status='Completed')

    context = {
        'employee': user_emp,
        'task_progress': task_progress_percentage.items(),
        'completed_task_assignees': completed_task_assignees,
    }

    return render(request, 'emp/emp_dashboard.html', context)


def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:  # Check if the user exists and is active
            login(request, user)
            if user.groups.filter(name__in=['HR', 'Manager']).exists():
                return redirect('emp:emp_home')
            else:
                return redirect('emp:my_tasks')
        else:
            message = 'Invalid username or password, or account is inactive.'
            return render(request, 'emp/login.html', {'error': message})
    else:
        return render(request, 'emp/login.html')


    
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task status and feedback updated successfully.')
        else:
            messages.error(request, 'Error updating task status and feedback.')
    else:
        form = TaskUpdateForm(instance=task)  # Add this line to handle GET request
    return render(request, 'emp/update_task_status.html', {'form': form, 'task': task})


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

# views.py
@login_required
def update_task_feedback(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.user.groups.filter(name='Manager').exists():  # Ensure only managers can update feedback
        if request.method == 'POST':
            feedback = request.POST.get('feedback', '').strip()
            task.feedback = feedback
            task.save()
            messages.success(request, 'Feedback updated successfully.')
        else:
            messages.error(request, 'Invalid request method.')
    else:
        messages.error(request, 'Unauthorized access.')
    return redirect('emp:hr_task_overview')  # Redirect back to the tasks overview


@login_required
def add_task_feedback(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        feedback_content = request.POST.get('feedback')
        if feedback_content:
            # Assuming Feedback is your model name and it has a task ForeignKey, content field, and created_by ForeignKey to User
            Feedback.objects.create(task=task, content=feedback_content, created_by=request.user)
            messages.success(request, 'Feedback added successfully.')
        else:
            messages.error(request, 'Feedback content cannot be empty.')
    return redirect('emp:hr_task_overview')


@login_required
def delete_task(request, task_id):
    if request.user.groups.filter(name='HR').exists():  # Check if the user is in HR
        task = Task.objects.get(pk=task_id)
        task.delete()
        messages.success(request, "Task deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete tasks.")
    return redirect('emp:hr_task_overview')  # Redirect to the tasks overview page

@login_required
def calendar_view(request):
    return render(request, 'emp/calendar.html')

# @login_required
# def event_data(request):
#     user_emp = request.user.emp if hasattr(request.user, 'emp') else None
#     # tasks = Task.objects.filter(assignees=user_emp)
#     sprints = Sprint.objects.filter(employees=user_emp)

#     # events = [
#     #     {'title': task.title, 'start': task.deadline.strftime('%Y-%m-%dT%H:%M:%S'), 'allDay': True}
#     #     for task in tasks
#     # ]
    
#     events += [
#         {'title': sprint.title, 'start': sprint.start_date.strftime('%Y-%m-%dT%H:%M:%S'),
#          'end': sprint.end_date.strftime('%Y-%m-%dT%H:%M:%S'), 'allDay': True}
#         for sprint in sprints
#     ]
#     if not events:
#         return JsonResponse({'message': 'No events found'}, status=404)
#     else:
#         return JsonResponse(events, safe=False)

@login_required
def event_data(request):
    # Check if the user is HR or Manager
    user_groups = request.user.groups.values_list('name', flat=True)
    is_hr_or_manager = any(group in user_groups for group in ['HR', 'Manager'])

    # Get sprints for HR/Manager or specific employee
    if is_hr_or_manager:
        sprints = Sprint.objects.all()
    else:
        user_emp = request.user.emp if hasattr(request.user, 'emp') else None
        if user_emp:
            sprints = Sprint.objects.filter(employees=user_emp)
        else:
            return JsonResponse({'message': 'User has no associated employee or is not authorized to view all sprints.'}, status=403)

    # Create events list from sprints
    events = [
        {'title': sprint.title, 'start': sprint.start_date.strftime('%Y-%m-%dT%H:%M:%S'),
         'end': sprint.end_date.strftime('%Y-%m-%dT%H:%M:%S'), 'allDay': True}
        for sprint in sprints
    ]

    # If no events found, send a 404 response
    if not events:
        return JsonResponse({'message': 'No events found'}, status=404)

    # Send events as JSON response
    return JsonResponse(events, safe=False)



@login_required
def add_sprint(request):
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('emp:calendar')  # Redirect to the calendar view where sprints are visible
    else:
        form = SprintForm()
    return render(request, 'emp/add_sprint.html', {'form': form})

@login_required
def messaging(request):
    contacts = User.objects.exclude(id=request.user.id)  # List other users
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('emp:messaging')  # Redirect back to the same messaging view
    else:
        form = MessageForm()
    return render(request, 'emp/messaging.html', {'messages': messages, 'contacts': contacts, 'form': form})

@login_required
def fetch_messages(request, user_id):
    # This is a simple example, adapt it according to your Message model structure
    messages = Message.objects.filter(
        sender_id=user_id, recipient=request.user
    ) | Message.objects.filter(
        sender=request.user, recipient_id=user_id
    )
    messages = messages.order_by('timestamp')
    # Serialize the messages into a JSON-friendly format
    messages_data = [{'content': message.message, 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for message in messages]
    return JsonResponse(messages_data, safe=False)


@login_required
@csrf_exempt  # This is for demonstration purposes. In production, you should handle CSRF properly.
@require_POST  # Ensure this view only accepts POST requests.
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient_id = data.get('recipient')
        message_text = data.get('message')
        
        # Assuming 'recipient_id' is the ID of the User model instance
        recipient = User.objects.get(pk=recipient_id)
        
        # Create and save the new message
        message = Message(sender=request.user, recipient=recipient, message=message_text)
        message.save()
        
        # Return a response, e.g., the message ID and a success status
        return JsonResponse({'id': message.id, 'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
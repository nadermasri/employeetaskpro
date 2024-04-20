from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Emp, Task, WhistleblowingCase, CaseConversation, Feedback, TaskAssignee,Sprint, Message, Meeting
from .forms import TaskAssignForm, WhistleblowingForm, ConversationForm, TaskForm,SprintForm, MessageForm, MeetingForm
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
from django.db.models import Q



@login_required
def emp_home(request):
    is_hr_or_manager = request.user.groups.filter(name__in=['HR', 'Manager']).exists()

    if not is_hr_or_manager:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('emp:emp_dashboard')

    # If the user is HR or Manager, show the employee tables
    emps = Emp.objects.all()
    # Iterate through each employee to calculate completed tasks count
    for emp in emps:
        tasks_assigned_to_employee = Task.objects.filter(taskassignee__emp=emp)
        completed_tasks_count = tasks_assigned_to_employee.filter(status='Completed').count()
        total_tasks_count = tasks_assigned_to_employee.count()
        progress_percentage = (completed_tasks_count / total_tasks_count) * 100 if total_tasks_count > 0 else 0
        emp.progress_percentage = progress_percentage

    context = {
        'emps': emps,
        'is_hr_or_manager': is_hr_or_manager,
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

        # Role assignment based on checkboxes
        if 'isHR' in request.POST:
            hr_group = Group.objects.get(name='HR')
            user.groups.add(hr_group)
        if 'isManager' in request.POST:
            manager_group = Group.objects.get(name='Manager')
            user.groups.add(manager_group)

        e = Emp(**form_data, user=user, date_added=timezone.now())
        e.save()

        messages.success(request, "Employee added successfully.")
        return render(request, 'emp/employee_success.html', {'username': user.username, 'password': plaintext_password})
    else:
        return render(request, "emp/add_emp.html", {})
def delete_emp(request, emp_id):
    emp = get_object_or_404(Emp, pk=emp_id)
    if emp.user:
        # Deactivate the user account associated with the employee
        emp.user.is_active = False
        emp.user.save()
        messages.success(request, f"Employee {emp.user.username}'s account has been deactivated.")
        # Now proceed to delete the employee record
        emp.delete()
        messages.success(request, f"Employee record for {emp.user.username} has been deleted.")
    else:
        # Notify if no user account is associated with the employee and delete only the employee record
        emp.delete()
        messages.success(request, "Employee record has been deleted, no user account was associated.")
    return redirect("/emp/home/")

@login_required
def update_emp(request, emp_id):
    emp = Emp.objects.get(pk=emp_id)
    # Determine group membership and pass this info to the template
    is_hr = emp.user.groups.filter(name="HR").exists()
    is_manager = emp.user.groups.filter(name="Manager").exists()

    context = {
        'emp': emp,
        'is_hr': is_hr,
        'is_manager': is_manager,
    }
    return render(request, "emp/update_emp.html", context)


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
        emp.status = "emp_status" in request.POST

        if emp.user:
            emp.user.is_active = emp.status
            update_user_roles(emp.user, request.POST)
            emp.user.save()

        emp.save()
        messages.success(request, "Employee updated successfully.")
        return redirect('/emp/home/')
    else:
        return render(request, "emp/update_emp.html", {'emp': emp})

def update_user_roles(user, post_data):
    hr_group = Group.objects.get(name='HR')
    manager_group = Group.objects.get(name='Manager')

    if 'isHR' in post_data and post_data['isHR'] == 'on':
        user.groups.add(hr_group)
    else:
        user.groups.remove(hr_group)

    if 'isManager' in post_data and post_data['isManager'] == 'on':
        user.groups.add(manager_group)
    else:
        user.groups.remove(manager_group)


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
        progress_input = request.POST.get('progress', 0)  # Default to 0 if not provided
        task_assignee = get_object_or_404(TaskAssignee, task_id=task_id, emp=user_emp)
        if new_status == 'Completed':
            task_assignee.progress = 100  # Automatically set progress to 100% if completed
            task_assignee.status = 'Completed'
            task_assignee.task.status='In Progress'
        elif new_status == 'In Progress' and int(progress_input) > 0:
            task_assignee.progress = int(progress_input)
            task_assignee.status = 'In Progress'
            task_assignee.task.status='In Progress'
        elif new_status == 'Not Started':
            task_assignee.progress = 0
            task_assignee.status = 'Not Started'
        
        task_assignee.save()
        task_assignee.task.save()
        return redirect('emp:my_tasks')  # Use path_info to reload the same page

    # Retrieve task assignees associated with the user
    task_assignees = TaskAssignee.objects.filter(emp=user_emp).exclude(status='Completed').select_related('task')

    if sort == 'urgency':
        task_assignees = task_assignees.order_by(Case(
            When(task__urgency='High', then=1),
            When(task__urgency='Medium', then=2),
            When(task__urgency='Low', then=3),
            default=4
        ))
    else:  # Default sort by deadline
        task_assignees = task_assignees.order_by('task__deadline')

    tasks_with_progress = [{
        'task_assignee': task_assignee,
        'progress': task_assignee.progress,
        'status': task_assignee.status
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
    tasks_with_progress = []
    for task in tasks:
        if task.status == 'In Progress':
            total_weight = sum(assignee.weight for assignee in task.taskassignee_set.all())
            if total_weight > 0:
                weighted_progress = sum(
                    assignee.weight * assignee.progress for assignee in task.taskassignee_set.all()
                )
                progress_percentage = weighted_progress / total_weight
                task.progress_percentage=progress_percentage
                task.save()
                if progress_percentage==100:
                    task.status='Completed'
                    task.save()
            else:
                progress_percentage = 0
            task.progress_display = f"{round(progress_percentage,2)}%"
        else:
            task.progress_display = task.status  # Not in progress, show status directly
        tasks_with_progress.append(task)

    context = {'tasks': tasks_with_progress}
    return render(request, 'emp/hr_task_overview.html', context)


@login_required
def emp_dashboard(request):
    user_emp = request.user.emp if hasattr(request.user, 'emp') else None

    # Retrieve task assignees associated with the user
    task_assignees = TaskAssignee.objects.filter(emp=user_emp).select_related('task')

    # Calculate task progress
    task_progress = {
        'Not Started': task_assignees.filter(status='Not Started').count(),
        'In Progress': task_assignees.filter(status='In Progress').count(),
        'Completed': task_assignees.filter(status='Completed').count(),
    }

    # Calculate percentages for each status
    total_tasks = sum(task_progress.values())
    task_progress_percentage = {status: round((count / total_tasks * 100), 2) if total_tasks > 0 else 0 for status, count in task_progress.items()}
    # Get completed tasks
    completed_task_assignees = task_assignees.filter(status='Completed')

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
            updated_task = form.save(commit=False)  # Get the instance without saving
            # Optionally, add any additional processing here
            updated_task.save()  # Save changes to the database
            messages.success(request, 'Task status updated successfully.')
            return redirect('your_success_view')
        else:
            messages.error(request, 'Form submission error.')
    else:
        form = TaskUpdateForm(instance=task)
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
    return redirect('emp:task_view_more', task_id)


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
    # Retrieve query parameters for filtering
    show_sprints = request.GET.get('showSprints', 'true') == 'true'
    show_meetings = request.GET.get('showMeetings', 'true') == 'true'
    show_tasks = request.GET.get('showTasks', 'true') == 'true'
    # Check if the user is HR or Manager
    user_groups = request.user.groups.values_list('name', flat=True)
    is_hr_or_manager = any(group in user_groups for group in ['HR', 'Manager'])

    events = []

    # Get sprints for HR/Manager or specific employee and append to events list
    if show_sprints:
        if is_hr_or_manager:
            sprints = Sprint.objects.all()
        else:
            user_emp = request.user.emp if hasattr(request.user, 'emp') else None
            sprints = Sprint.objects.filter(employees=user_emp) if user_emp else []

        events.extend([
            {'title': sprint.title, 'start': sprint.start_date.strftime('%Y-%m-%dT%H:%M:%S'),
             'end': sprint.end_date.strftime('%Y-%m-%dT%H:%M:%S'), 'allDay': True,'color': '#D87889' ,
                     'extendedProps': {
            'description': sprint.description,
             # Replace with actual property names
        }
             }
            for sprint in sprints
        ])

    # Get meetings for HR/Manager or specific employee and append to events list
    if show_meetings:
        if is_hr_or_manager:
            meetings = Meeting.objects.all()
        else:
            user_emp = request.user.emp if hasattr(request.user, 'emp') else None
            meetings = Meeting.objects.filter(participants=user_emp) if user_emp else []

        events.extend([
            {
                'title': meeting.title,
                'start': meeting.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'end': meeting.end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'allDay': False, # or True, based on your model definition
                  'extendedProps': {
            'description': meeting.description,
             # Replace with actual property names
        }
            } for meeting in meetings
        ])
    if show_tasks:
        if is_hr_or_manager:
            tasks = Task.objects.all()
        else:
            user_emp = request.user.emp if hasattr(request.user, 'emp') else None
            tasks = Task.objects.filter(taskassignee__emp=user_emp) if user_emp else []
        events.extend([
            {
                'title': f"Task Deadline: {task.title}",
                'start': task.deadline.strftime('%Y-%m-%dT%H:%M:%S'),
                'allDay': True,
                'backgroundColor': '#ff9f89',  # You can set a custom color for task deadlines
                'borderColor': '#ff9f89',
                  'extendedProps': {
            'description': task.description,
             # Replace with actual property names
        }
            } for task in tasks if task.deadline  # Only include tasks with a deadline
        ])
    # Send events as JSON response
    return JsonResponse(events, safe=False)


@login_required
def get_task_employees(request, task_id):
    if request.method == 'GET':
        employees = Emp.objects.filter(taskassignee__task_id=task_id).values('id', 'firstname', 'lastname')
        return JsonResponse(list(employees), safe=False)
    return JsonResponse({'error': 'Request must be GET'}, status=400)

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

@login_required
def add_meeting(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            
            # Check for overlapping meetings
            participants = form.cleaned_data.get('participants')
            overlapping_meetings = Meeting.objects.filter(
                Q(participants__in=participants) & 
                (Q(start_time__lt=meeting.end_time) & Q(end_time__gt=meeting.start_time))
            ).distinct()
            print("IM HERE")
            if overlapping_meetings.exists():
                # Handle the overlap situation, e.g., by returning an error message
                print("OVERLAPPINGG")
                messages.error(request, "One or more participants are not available in the given time slot.")
                return render(request, 'emp/add_meeting.html', {'form': form})
            print()
            # No overlaps, safe to save
            meeting.save()
            form.save_m2m()
            messages.success(request, "Meeting scheduled successfully.")
            return redirect('emp:calendar')
    else:
        form = MeetingForm()

    return render(request, "emp/add_meeting.html", {'form': form})

@login_required
def task_view_more(request, task_id):
    # Retrieve the task using the task_id
    task = get_object_or_404(Task, pk=task_id)

    # Get all assignees related to this task
    assignees = TaskAssignee.objects.filter(task=task).select_related('emp')
    # Get all feedback related to this task
    feedbacks = Feedback.objects.filter(task=task)

    # Calculating the sum of all feedbacks and assignees
    total_feedbacks = feedbacks.count()
    total_assignees = assignees.count()

    context = {
        'id':task_id,
        'task': task,
        'assignees': assignees,
        'feedbacks': feedbacks,
        'total_feedbacks': total_feedbacks,
        'total_assignees': total_assignees,
    }

    return render(request, 'emp/task_view_more.html', context)

@login_required
def toggle_hr_manager(request, emp_id, group_name):
    emp = get_object_or_404(Emp, pk=emp_id)
    group = Group.objects.get(name=group_name)
    user = emp.user

    if group in user.groups.all():
        user.groups.remove(group)
        message = f'Removed {user.username} from {group_name}.'
    else:
        user.groups.add(group)
        message = f'Added {user.username} to {group_name}.'

    messages.success(request, message)
    return redirect('emp:emp_details', emp_id=emp.id)  # Assuming there's an employee details view to return tos
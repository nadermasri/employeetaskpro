# emp/context_processors.py

def user_roles(request):
    is_hr_or_manager = request.user.groups.filter(name__in=['HR', 'Manager']).exists()
    is_employee = request.user.groups.filter(name='Employee').exists()
    
    return {
        'is_hr_or_manager': is_hr_or_manager,
        'is_employee': is_employee,
    }

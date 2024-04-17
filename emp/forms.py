from django import forms
from .models import Task, Emp, WhistleblowingCase, CaseConversation, TaskAssignee
from django_select2 import forms as s2forms
from django.forms import DateTimeInput

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'urgency']
        widgets = {
            'deadline': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        initial_deadline = self.initial.get('deadline')
        if initial_deadline:
            # Format the date to match the datetime-local input requirements
            self.initial['deadline'] = initial_deadline.strftime('%Y-%m-%dT%H:%M')

class TaskAssignForm(forms.ModelForm):
    emp = forms.ModelChoiceField(
        queryset=Emp.objects.all(),
        label="Employee",
        required=True
    )
    weight = forms.IntegerField(min_value=1, max_value=100, help_text="Percentage of responsibility")

    class Meta:
        model = TaskAssignee
        fields = ['emp', 'weight']

    def __init__(self, *args, **kwargs):
        super(TaskAssignForm, self).__init__(*args, **kwargs)
        # Assuming you might want to filter employees or make adjustments based on the instance
        if 'instance' in kwargs:
            self.fields['emp'].queryset = Emp.objects.exclude(id=kwargs['instance'].emp.id)


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status', 'feedback']  # Add 'feedback' here

    def __init__(self, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'this.form.submit()',
        })
        self.fields['feedback'].widget = forms.Textarea(attrs={'rows': 3})  # Add this line to customize the textarea


class WhistleblowingForm(forms.ModelForm):
    class Meta:
        model = WhistleblowingCase
        fields = ['involved_employees', 'description', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ConversationForm(forms.ModelForm):
    class Meta:
        model = CaseConversation
        fields = ['message']


from django import forms
from .models import Task

class TaskAssignForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'deadline', 'urgency']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskAssignForm, self).__init__(*args, **kwargs)
class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'this.form.submit()',
        })

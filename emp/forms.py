from django import forms
from .models import Task, Emp, WhistleblowingCase, CaseConversation
from django_select2 import forms as s2forms




class TaskAssignForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignees', 'deadline', 'urgency']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'assignees': s2forms.Select2MultipleWidget,
        }

    def __init__(self, *args, **kwargs):
        super(TaskAssignForm, self).__init__(*args, **kwargs)
        self.fields['assignees'].queryset = Emp.objects.all()  # Or any other queryset you wish to use
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


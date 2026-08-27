from django import forms
from django.db import models

from core.forms import StyledFormMixin

from .models import Comment, Tag, Task


class TaskForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assignee', 'status', 'priority', 'due_date', 'estimated_hours', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Task description...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 4.5', 'step': '0.5', 'min': '0'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from projects.models import Project
            self.fields['project'].queryset = Project.objects.filter(
                models.Q(owner=user) | models.Q(team_members=user) | models.Q(memberships__user=user)
            ).distinct()

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get('project')
        assignee = cleaned.get('assignee')
        if project and assignee:
            if not project.team_members.filter(id=assignee.id).exists() and project.owner != assignee:
                self.add_error('assignee', 'Assignee must be a team member of the selected project.')
        return cleaned


class TaskFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input form-input-sm', 'placeholder': 'Search tasks...'}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Task.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    assignee = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    tag = forms.ModelChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    due_before = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input form-input-sm', 'type': 'date'}),
    )
    due_after = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input form-input-sm', 'type': 'date'}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest first'),
            ('created_at', 'Oldest first'),
            ('due_date', 'Due date (ascending)'),
            ('-due_date', 'Due date (descending)'),
            ('priority', 'Priority (low first)'),
            ('-priority', 'Priority (high first)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )


class CommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-textarea form-textarea-sm', 'rows': 3, 'placeholder': 'Write a comment...'}),
        }


class TaskStatusForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

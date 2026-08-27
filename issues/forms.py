from django import forms
from django.db import models

from core.forms import StyledFormMixin

from .models import Issue, IssueComment


class IssueForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'project', 'assignee', 'status', 'priority', 'severity', 'due_date', 'steps_to_reproduce', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Issue title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Issue description...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'steps_to_reproduce': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Steps to reproduce...'}),
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


class IssueFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input form-input-sm', 'placeholder': 'Search issues...'}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Issue.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + Issue.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'All Severities')] + Issue.SEVERITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    assignee = forms.ChoiceField(
        required=False,
        choices=[],
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


class IssueStatusForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }


class IssueCommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-textarea form-textarea-sm', 'rows': 3, 'placeholder': 'Write a comment...'}),
        }


class IssueResolutionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['resolution']
        widgets = {
            'resolution': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Describe the resolution...'}),
        }

from django import forms
from django.utils import timezone

from core.forms import StyledFormMixin

from .models import Project, ProjectMembership


class ProjectForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'priority', 'start_date', 'due_date', 'team_members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Project name'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Project description...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        due = cleaned.get('due_date')
        if start and due and start > due:
            self.add_error('due_date', 'Due date must be after start date.')
        return cleaned


class ProjectFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input form-input-sm', 'placeholder': 'Search projects...'}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Project.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + Project.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest first'),
            ('created_at', 'Oldest first'),
            ('due_date', 'Due date (ascending)'),
            ('-due_date', 'Due date (descending)'),
            ('name', 'Name (A-Z)'),
            ('-name', 'Name (Z-A)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )


class ProjectMemberForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectMembership
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            existing_ids = list(project.memberships.values_list('user_id', flat=True))
            existing_ids.append(project.owner_id)
            from accounts.models import User
            self.fields['user'].queryset = User.objects.exclude(pk__in=existing_ids)

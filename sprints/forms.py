from django import forms
from django.db import models

from core.forms import StyledFormMixin
from projects.models import Project

from .models import Sprint


class SprintForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['project', 'name', 'goal', 'start_date', 'end_date', 'status']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Sprint name'}),
            'goal': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Sprint goal (optional)'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(
                models.Q(owner=user) | models.Q(team_members=user) | models.Q(memberships__user=user)
            ).distinct()

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned


class AddTaskToSprintForm(forms.Form):
    """Form to select a task to add to a sprint."""
    task = forms.IntegerField(widget=forms.HiddenInput())

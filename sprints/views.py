from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from projects.models import Project
from tasks.models import Task

from .forms import SprintForm
from .models import Sprint, SprintTask


class SprintListView(LoginRequiredMixin, ListView):
    model = Sprint
    template_name = 'sprints/sprint_list.html'
    context_object_name = 'sprints'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        return Sprint.objects.filter(
            Q(project__owner=user)
            | Q(project__team_members=user)
            | Q(project__memberships__user=user)
        ).select_related('project').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_filter'] = self.request.GET.get('status', '')
        if context['active_filter']:
            context['sprints'] = context['sprints'].filter(status=context['active_filter'])
        context['projects'] = Project.objects.filter(
            Q(owner=self.request.user) | Q(team_members=self.request.user)
        ).distinct()
        return context


class SprintDetailView(LoginRequiredMixin, DetailView):
    model = Sprint
    template_name = 'sprints/sprint_detail.html'
    context_object_name = 'sprint'

    def get_queryset(self):
        user = self.request.user
        return Sprint.objects.filter(
            Q(project__owner=user)
            | Q(project__team_members=user)
            | Q(project__memberships__user=user)
        ).select_related('project').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sprint = self.object

        status_colors = {
            'todo': '#7b8da4',
            'in_progress': '#1083e0',
            'in_review': '#8b5cf6',
            'completed': '#7dcd30',
            'blocked': '#ef4444',
        }

        sprint_tasks = sprint.sprint_tasks.select_related(
            'task', 'task__assignee', 'task__assigned_by', 'task__project'
        ).order_by('task__status', 'task__priority', 'task__title')

        # Build list of (status_code, label, color, tasks_list)
        columns_with_tasks = []
        for status_code, status_label in Task.STATUS_CHOICES:
            color = status_colors[status_code]
            col_tasks = [st for st in sprint_tasks if st.task.status == status_code]
            columns_with_tasks.append((status_code, status_label, color, col_tasks))

        context['columns_with_tasks'] = columns_with_tasks

        # Available tasks: from same project, not already in this sprint
        sprint_task_ids = sprint.sprint_tasks.values_list('task_id', flat=True)
        project = sprint.project
        context['available_tasks'] = Task.objects.filter(
            project=project
        ).exclude(id__in=sprint_task_ids).select_related('assignee').order_by('title')

        context['can_edit'] = (
            self.request.user == project.owner
            or self.request.user.is_superuser
            or project.user_can_edit(self.request.user)
        )
        return context


class SprintCreateView(LoginRequiredMixin, CreateView):
    model = Sprint
    form_class = SprintForm
    template_name = 'sprints/sprint_form.html'

    def form_valid(self, form):
        form.instance.project = form.cleaned_data['project']
        messages.success(self.request, 'Sprint created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sprints:detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SprintUpdateView(LoginRequiredMixin, UpdateView):
    model = Sprint
    form_class = SprintForm
    template_name = 'sprints/sprint_form.html'

    def form_valid(self, form):
        new_status = form.cleaned_data.get('status')
        sprint = self.object

        if new_status == 'active' and sprint.status != 'active':
            sprint.activate()
            messages.success(self.request, f'"{sprint.name}" is now the active sprint.')
        else:
            messages.success(self.request, 'Sprint updated successfully.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sprints:detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SprintDeleteView(LoginRequiredMixin, DeleteView):
    model = Sprint
    template_name = 'sprints/sprint_confirm_delete.html'
    success_url = reverse_lazy('sprints:list')

    def form_valid(self, form):
        messages.success(self.request, f'Sprint "{self.object.name}" deleted.')
        return super().form_valid(form)


class AddTaskToSprintView(LoginRequiredMixin, View):
    """Add a task to a sprint via POST."""

    def post(self, request, pk):
        sprint = get_object_or_404(Sprint, pk=pk)
        task_id = request.POST.get('task_id')
        if not task_id:
            return JsonResponse({'error': 'No task specified.'}, status=400)

        task = get_object_or_404(Task, pk=task_id)
        if task.project != sprint.project:
            return JsonResponse({'error': 'Task is not from the sprint project.'}, status=400)

        sprint_task, created = SprintTask.objects.get_or_create(sprint=sprint, task=task)
        if created:
            return JsonResponse({'success': True, 'task_id': task.pk})
        return JsonResponse({'error': 'Task is already in this sprint.'}, status=400)


class RemoveTaskFromSprintView(LoginRequiredMixin, View):
    """Remove a task from a sprint via POST."""

    def post(self, request, pk, task_pk):
        sprint = get_object_or_404(Sprint, pk=pk)
        deleted, _ = SprintTask.objects.filter(sprint=sprint, task_id=task_pk).delete()
        if deleted:
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Task not found in sprint.'}, status=404)

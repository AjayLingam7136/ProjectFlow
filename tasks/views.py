import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, TemplateView, UpdateView
)

from activity.utils import log_activity
from .forms import CommentForm, TaskFilterForm, TaskForm, TaskStatusForm
from .models import Comment, Task

User = get_user_model()


class TaskListView(LoginRequiredMixin, TemplateView):
    """Kanban board view for tasks — default list view."""
    template_name = 'tasks/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from projects.models import Project
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user)
        ).distinct()

        project_id = self.request.GET.get('project')
        tasks_qs = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).select_related('project', 'assignee').prefetch_related('tags').distinct()

        if project_id:
            tasks_qs = tasks_qs.filter(project_id=project_id)
            context['selected_project'] = int(project_id)

        context['projects'] = projects
        context['columns'] = [
            ('todo', 'To Do', tasks_qs.filter(status='todo').order_by('order', '-created_at')),
            ('in_progress', 'In Progress', tasks_qs.filter(status='in_progress').order_by('order', '-created_at')),
            ('in_review', 'In Review', tasks_qs.filter(status='in_review').order_by('order', '-created_at')),
            ('completed', 'Done', tasks_qs.filter(status='completed').order_by('order', '-created_at')),
        ]
        context['filter_form'] = TaskFilterForm(self.request.GET)
        context['board_type'] = 'tasks'
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['task_status_form'] = TaskStatusForm(instance=self.object)
        context['user_role'] = self.object.project.get_user_role(self.request.user)
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, 'create_task', f'Created task "{self.object.title}"', self.object)
        if self.object.assignee and self.object.assignee != self.request.user:
            log_activity(self.request.user, 'assign_task', f'Assigned task "{self.object.title}" to {self.object.assignee.get_full_name() or self.object.assignee.username}', self.object)
        messages.success(self.request, 'Task created successfully.')
        return response

    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    raise_exception = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        task = self.get_object()
        project = task.project
        return (
            project.owner == self.request.user
            or task.created_by == self.request.user
            or project.user_can_edit(self.request.user)
        )

    def form_valid(self, form):
        old_status = self.get_object().status
        response = super().form_valid(form)
        log_activity(self.request.user, 'update_task', f'Updated task "{self.object.title}"', self.object)
        if old_status != self.object.status:
            log_activity(self.request.user, 'change_status', f'Changed task "{self.object.title}" status to {self.object.get_status_display()}', self.object)
        messages.success(self.request, 'Task updated successfully.')
        return response

    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')
    raise_exception = True

    def test_func(self):
        task = self.get_object()
        project = task.project
        return (
            project.owner == self.request.user
            or task.created_by == self.request.user
            or project.user_can_edit(self.request.user)
        )

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        log_activity(request.user, 'delete_task', f'Deleted task "{task.title}" from {task.project.name}', task)
        messages.success(self.request, 'Task deleted successfully.')
        return super().delete(request, *args, **kwargs)


class TaskStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskStatusForm
    template_name = 'tasks/task_status_partial.html'

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Task status updated.')
        return response

    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        task = Task.objects.get(pk=self.kwargs['pk'])
        form.instance.task = task
        form.instance.author = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, 'add_comment', f'Commented on task "{task.title}"', task)
        messages.success(self.request, 'Comment added.')
        return response

    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.kwargs['pk']})


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'tasks/comment_edit.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.task.project.user_can_edit(self.request.user)

    def form_valid(self, form):
        form.instance.edited_at = timezone.now()
        messages.success(self.request, 'Comment updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.task.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'tasks/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.task.project.user_can_edit(self.request.user)

    def form_valid(self, form):
        task = self.get_object().task
        messages.success(self.request, 'Comment deleted.')
        return super().form_valid(form)

    def get_success_url(self):
        comment = self.object
        return reverse('tasks:detail', kwargs={'pk': comment.task.pk})


class TaskBulkStatusUpdateView(LoginRequiredMixin, View):
    """AJAX endpoint for batch status changes."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        task_ids = data.get('task_ids', [])
        new_status = data.get('status')

        if not task_ids or new_status not in dict(Task.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

        user = request.user
        tasks = Task.objects.filter(
            pk__in=task_ids,
        ).filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assignee=user)
        ).distinct()

        updated = tasks.update(status=new_status)
        return JsonResponse({'success': True, 'updated': updated})


class TaskReorderView(LoginRequiredMixin, View):
    """AJAX endpoint for reordering tasks within a status column."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        task_orders = data.get('orders', [])

        user = request.user
        for item in task_orders:
            task_id = item.get('id')
            order = item.get('order', 0)
            Task.objects.filter(
                pk=task_id,
            ).filter(
                Q(project__owner=user) | Q(project__team_members=user) | Q(assignee=user)
            ).update(order=order)

        return JsonResponse({'success': True})


class TaskAPIView(LoginRequiredMixin, View):
    """JSON endpoint for task data (used by Kanban)."""

    def get(self, request):
        user = request.user
        qs = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

        # Optional filters
        project_id = request.GET.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)

        status_filter = request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        priority_filter = request.GET.get('priority')
        if priority_filter:
            qs = qs.filter(priority=priority_filter)

        assignee_filter = request.GET.get('assignee')
        if assignee_filter:
            qs = qs.filter(assignee_id=assignee_filter)

        tasks = []
        for task in qs.select_related('project', 'assignee').prefetch_related('tags').order_by('order', '-created_at'):
            tasks.append({
                'id': task.pk,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'assignee': {
                    'id': task.assignee.pk,
                    'name': task.assignee.get_full_name() or task.assignee.username,
                    'initials': task.assignee.get_initials,
                } if task.assignee else None,
                'project': {
                    'id': task.project.pk,
                    'name': task.project.name,
                },
                'tags': [{'id': t.pk, 'name': t.name, 'color': t.color} for t in task.tags.all()],
                'is_overdue': task.is_overdue,
                'order': task.order,
            })

        return JsonResponse({'tasks': tasks})


class KanbanBoardView(LoginRequiredMixin, View):
    """Redirect to the task list view (kanban is now the default)."""

    def get(self, request, *args, **kwargs):
        return redirect('tasks:list')


class KanbanTaskMoveView(LoginRequiredMixin, View):
    """Handle drag-drop task status change and reorder."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        task_id = data.get('task_id')
        new_status = data.get('status')
        new_order = data.get('order', 0)

        if not task_id or new_status not in dict(Task.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

        user = request.user
        task = Task.objects.filter(
            pk=task_id,
        ).filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assignee=user)
        ).first()

        if not task:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

        old_status = task.status
        task.status = new_status
        task.order = new_order
        task.save(update_fields=['status', 'order'])

        if old_status != new_status:
            from activity.utils import log_activity
            log_activity(user, 'change_status', f'Changed task "{task.title}" status to {task.get_status_display()}', task)

        return JsonResponse({'success': True})

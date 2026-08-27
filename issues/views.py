import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, TemplateView, UpdateView
)

from activity.utils import log_activity
from .forms import (
    IssueCommentForm, IssueFilterForm, IssueForm,
    IssueResolutionForm, IssueStatusForm,
)
from .models import Issue, IssueComment

User = get_user_model()


class IssueListView(LoginRequiredMixin, TemplateView):
    """Kanban board view for issues — default list view."""
    template_name = 'issues/issue_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from projects.models import Project
        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user)
        ).distinct()

        project_id = self.request.GET.get('project')
        issues_qs = Issue.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).select_related('project', 'assignee').prefetch_related('tags').distinct()

        if project_id:
            issues_qs = issues_qs.filter(project_id=project_id)
            context['selected_project'] = int(project_id)

        context['projects'] = projects
        context['columns'] = [
            ('open', 'Open', issues_qs.filter(status='open').order_by('order', '-created_at')),
            ('assigned', 'Assigned', issues_qs.filter(status='assigned').order_by('order', '-created_at')),
            ('in_progress', 'In Progress', issues_qs.filter(status='in_progress').order_by('order', '-created_at')),
            ('fixed', 'Fixed', issues_qs.filter(status='fixed').order_by('order', '-created_at')),
            ('closed', 'Closed', issues_qs.filter(status='closed').order_by('order', '-created_at')),
            ('reopen', 'Reopen', issues_qs.filter(status='reopen').order_by('order', '-created_at')),
        ]
        context['filter_form'] = IssueFilterForm(self.request.GET)
        context['board_type'] = 'issues'
        return context


class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = 'issues/issue_detail.html'
    context_object_name = 'issue'

    def get_queryset(self):
        user = self.request.user
        return Issue.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = IssueCommentForm()
        context['issue_status_form'] = IssueStatusForm(instance=self.object)
        context['issue_resolution_form'] = IssueResolutionForm(instance=self.object)
        context['user_role'] = self.object.project.get_user_role(self.request.user)
        return context


class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'issues/issue_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, 'create_issue', f'Created issue "{self.object.title}"', self.object)
        if self.object.assignee and self.object.assignee != self.request.user:
            log_activity(self.request.user, 'assign_issue', f'Assigned issue "{self.object.title}" to {self.object.assignee.get_full_name() or self.object.assignee.username}', self.object)
        messages.success(self.request, 'Issue created successfully.')
        return response

    def get_success_url(self):
        return reverse('issues:detail', kwargs={'pk': self.object.pk})


class IssueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'issues/issue_form.html'
    raise_exception = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        issue = self.get_object()
        project = issue.project
        return (
            project.owner == self.request.user
            or issue.created_by == self.request.user
            or project.user_can_edit(self.request.user)
        )

    def form_valid(self, form):
        old_status = self.get_object().status
        response = super().form_valid(form)
        log_activity(self.request.user, 'update_issue', f'Updated issue "{self.object.title}"', self.object)
        if old_status != self.object.status:
            log_activity(self.request.user, 'change_issue_status', f'Changed issue "{self.object.title}" status to {self.object.get_status_display()}', self.object)
        messages.success(self.request, 'Issue updated successfully.')
        return response

    def get_success_url(self):
        return reverse('issues:detail', kwargs={'pk': self.object.pk})


class IssueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Issue
    template_name = 'issues/issue_confirm_delete.html'
    success_url = reverse_lazy('issues:list')
    raise_exception = True

    def test_func(self):
        issue = self.get_object()
        project = issue.project
        return (
            project.owner == self.request.user
            or issue.created_by == self.request.user
            or project.user_can_edit(self.request.user)
        )

    def delete(self, request, *args, **kwargs):
        issue = self.get_object()
        log_activity(request.user, 'delete_issue', f'Deleted issue "{issue.title}" from {issue.project.name}', issue)
        messages.success(self.request, 'Issue deleted successfully.')
        return super().delete(request, *args, **kwargs)


class IssueStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueStatusForm

    def get_queryset(self):
        user = self.request.user
        return Issue.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Issue status updated.')
        return response

    def get_success_url(self):
        return reverse('issues:detail', kwargs={'pk': self.object.pk})


class IssueResolutionUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueResolutionForm

    def get_queryset(self):
        user = self.request.user
        return Issue.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Resolution updated.')
        return response

    def get_success_url(self):
        return reverse('issues:detail', kwargs={'pk': self.object.pk})


class IssueCommentCreateView(LoginRequiredMixin, CreateView):
    model = IssueComment
    form_class = IssueCommentForm

    def form_valid(self, form):
        issue = Issue.objects.get(pk=self.kwargs['pk'])
        form.instance.issue = issue
        form.instance.author = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, 'add_comment', f'Commented on issue "{issue.title}"', issue)
        messages.success(self.request, 'Comment added.')
        return response

    def get_success_url(self):
        return reverse('issues:detail', kwargs={'pk': self.kwargs['pk']})


class IssueCommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = IssueComment
    form_class = IssueCommentForm
    template_name = 'issues/comment_edit.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.issue.project.user_can_edit(self.request.user)

    def form_valid(self, form):
        form.instance.edited_at = timezone.now()
        messages.success(self.request, 'Comment updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('issues:detail', kwargs={'pk': self.object.issue.pk})


class IssueCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = IssueComment
    template_name = 'issues/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.issue.project.user_can_edit(self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Comment deleted.')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        comment = self.object
        return reverse('issues:detail', kwargs={'pk': comment.issue.pk})


class IssueAPIView(LoginRequiredMixin, View):
    """JSON endpoint for issue data (used by Kanban)."""

    def get(self, request):
        user = request.user
        qs = Issue.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user) | Q(assignee=user)
        ).distinct()

        project_id = request.GET.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)

        issues = []
        for issue in qs.select_related('project', 'assignee').prefetch_related('tags').order_by('order', '-created_at'):
            issues.append({
                'id': issue.pk,
                'title': issue.title,
                'status': issue.status,
                'priority': issue.priority,
                'severity': issue.severity,
                'due_date': issue.due_date.isoformat() if issue.due_date else None,
                'assignee': {
                    'id': issue.assignee.pk,
                    'name': issue.assignee.get_full_name() or issue.assignee.username,
                    'initials': issue.assignee.get_initials,
                } if issue.assignee else None,
                'project': {
                    'id': issue.project.pk,
                    'name': issue.project.name,
                },
                'tags': [{'id': t.pk, 'name': t.name, 'color': t.color} for t in issue.tags.all()],
                'is_overdue': issue.is_overdue,
                'order': issue.order,
            })

        return JsonResponse({'issues': issues})


class IssueKanbanMoveView(LoginRequiredMixin, View):
    """Handle drag-drop issue status change and reorder."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        issue_id = data.get('issue_id') or data.get('task_id')
        new_status = data.get('status')
        new_order = data.get('order', 0)

        if not issue_id or new_status not in dict(Issue.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

        user = request.user
        issue = Issue.objects.filter(
            pk=issue_id,
        ).filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assignee=user)
        ).first()

        if not issue:
            return JsonResponse({'success': False, 'error': 'Issue not found'}, status=404)

        old_status = issue.status
        issue.status = new_status
        issue.order = new_order
        issue.save(update_fields=['status', 'order'])

        if old_status != new_status:
            log_activity(user, 'change_issue_status', f'Changed issue "{issue.title}" status to {issue.get_status_display()}', issue)

        return JsonResponse({'success': True})


class IssueBulkStatusUpdateView(LoginRequiredMixin, View):
    """AJAX endpoint for batch status changes."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        issue_ids = data.get('issue_ids', []) or data.get('task_ids', [])
        new_status = data.get('status')

        if not issue_ids or new_status not in dict(Issue.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

        user = request.user
        issues = Issue.objects.filter(
            pk__in=issue_ids,
        ).filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(assignee=user)
        ).distinct()

        updated = issues.update(status=new_status)
        return JsonResponse({'success': True, 'updated': updated})

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from activity.utils import log_activity
from .forms import ProjectFilterForm, ProjectForm, ProjectMemberForm
from .mixins import ProjectManagerMixin, ProjectOwnerOrAdminMixin, ProjectPermissionMixin
from .models import Project, ProjectBookmark, ProjectMembership


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ProjectFilterForm(self.request.GET)
        return context


class ProjectDetailView(LoginRequiredMixin, ProjectPermissionMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    required_roles = None

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        context['user_role'] = project.get_user_role(user)
        context['memberships'] = project.memberships.select_related('user').all()
        context['is_bookmarked'] = ProjectBookmark.objects.filter(user=user, project=project).exists()

        # Task summary by status
        from tasks.models import Task
        tasks = project.tasks.all()
        context['task_summary'] = {
            'total': tasks.count(),
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'completed': tasks.filter(status='completed').count(),
            'blocked': tasks.filter(status='blocked').count(),
        }

        # Upcoming milestones (tasks with due dates, not completed)
        context['upcoming_milestones'] = tasks.filter(
            due_date__isnull=False,
            status__in=['todo', 'in_progress', 'in_review'],
        ).order_by('due_date')[:10]

        # Overdue tasks
        context['overdue_tasks'] = tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=['todo', 'in_progress', 'in_review', 'blocked'],
        ).count()

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role='admin',
        )
        log_activity(self.request.user, 'create_project', f'Created project "{self.object.name}"', self.object)
        messages.success(self.request, 'Project created successfully.')
        return response

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, ProjectManagerMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, 'update_project', f'Updated project "{self.object.name}"', self.object)
        messages.success(self.request, 'Project updated successfully.')
        return response

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, ProjectOwnerOrAdminMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:list')

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        log_activity(request.user, 'delete_project', f'Deleted project "{project.name}"', project)
        messages.success(self.request, 'Project deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ProjectMembersView(LoginRequiredMixin, ProjectPermissionMixin, DetailView):
    model = Project
    template_name = 'projects/members.html'
    context_object_name = 'project'
    required_roles = None

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context['memberships'] = project.memberships.select_related('user').all()
        context['user_role'] = project.get_user_role(self.request.user)
        context['member_form'] = ProjectMemberForm(project=project)
        return context


class ProjectMemberAddView(LoginRequiredMixin, ProjectManagerMixin, View):
    def get_project(self):
        return Project.objects.get(pk=self.kwargs['pk'])

    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        form = ProjectMemberForm(project=project, data=request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.project = project
            membership.save()
            project.team_members.add(membership.user)
            log_activity(request.user, 'add_team_member', f'Added {membership.user.get_full_name() or membership.user.username} to the project as {membership.get_role_display()}', project)
            messages.success(request, f'{membership.user.get_full_name() or membership.user.username} added to the project.')
            return redirect(reverse('projects:members', kwargs={'pk': pk}))
        context = {
            'project': project,
            'memberships': project.memberships.select_related('user').all(),
            'user_role': project.get_user_role(request.user),
            'member_form': form,
        }
        return render(request, 'projects/members.html', context)


class ProjectMemberRoleUpdateView(LoginRequiredMixin, ProjectManagerMixin, View):
    def get_project(self):
        return Project.objects.get(pk=self.kwargs['pk'])

    def post(self, request, pk, member_id):
        project = Project.objects.get(pk=pk)
        membership = ProjectMembership.objects.get(pk=member_id, project=project)
        new_role = request.POST.get('role')
        valid_roles = [r[0] for r in ProjectMembership.ROLE_CHOICES]
        if new_role not in valid_roles:
            messages.error(request, 'Invalid role.')
            return redirect(reverse('projects:members', kwargs={'pk': pk}))
        membership.role = new_role
        membership.save()
        log_activity(request.user, 'change_role', f'Changed {membership.user.get_full_name() or membership.user.username} role to {membership.get_role_display()}', project)
        messages.success(request, f'{membership.user.get_full_name() or membership.user.username} role updated to {membership.get_role_display()}.')
        return redirect(reverse('projects:members', kwargs={'pk': pk}))


class ProjectMemberRemoveView(LoginRequiredMixin, ProjectManagerMixin, View):
    def get_project(self):
        return Project.objects.get(pk=self.kwargs['pk'])

    def post(self, request, pk, member_id):
        project = Project.objects.get(pk=pk)
        membership = ProjectMembership.objects.get(pk=member_id, project=project)
        user_name = membership.user.get_full_name() or membership.user.username
        membership.delete()
        project.team_members.remove(membership.user)
        log_activity(request.user, 'remove_team_member', f'Removed {user_name} from the project', project)
        messages.success(request, f'{user_name} removed from the project.')
        return redirect(reverse('projects:members', kwargs={'pk': pk}))


class ProjectBookmarkToggleView(LoginRequiredMixin, View):
    """Toggle bookmark/star on a project."""

    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        bookmark, created = ProjectBookmark.objects.get_or_create(user=request.user, project=project)
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
        return JsonResponse({'success': True, 'is_bookmarked': is_bookmarked})

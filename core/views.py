from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from projects.models import Project
from tasks.models import Task
from issues.models import Issue


def page_not_found(request, exception=None):
    return render(request, 'core/404.html', status=404)


def server_error(request):
    return render(request, 'core/500.html', status=500)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        next_week = today + timedelta(days=7)

        # Projects the user owns or is a team member of
        user_projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user)
        ).distinct()

        # Tasks assigned to the user or in user's projects
        user_tasks = Task.objects.filter(
            Q(assignee=user) | Q(project__in=user_projects)
        ).distinct()

        # Summary statistics
        context['total_projects'] = user_projects.count()
        context['active_projects'] = user_projects.exclude(status='completed').exclude(status='cancelled').count()
        context['total_tasks'] = user_tasks.count()
        context['active_tasks'] = user_tasks.exclude(status='completed').count()
        context['overdue_tasks'] = user_tasks.filter(
            due_date__lt=today
        ).exclude(status='completed').count()
        context['completed_tasks'] = user_tasks.filter(status='completed').count()

        # Project cards for dashboard
        context['projects'] = user_projects.order_by('-created_at')[:8]

        # Upcoming deadlines (overdue + tasks due within next 7 days)
        context['upcoming_tasks'] = user_tasks.filter(
            Q(due_date__lt=today) | Q(due_date__range=[today, next_week])
        ).exclude(status='completed').order_by('due_date')

        # Issues assigned to the user or in user's projects
        user_issues = Issue.objects.filter(
            Q(assignee=user) | Q(project__in=user_projects)
        ).distinct()

        context['total_issues'] = user_issues.count()
        context['active_issues'] = user_issues.exclude(status='completed').count()
        context['overdue_issues'] = user_issues.filter(
            due_date__lt=today
        ).exclude(status='completed').count()
        context['completed_issues'] = user_issues.filter(status='completed').count()

        # Upcoming issue deadlines (overdue + issues due within next 7 days)
        context['upcoming_issues'] = user_issues.filter(
            Q(due_date__lt=today) | Q(due_date__range=[today, next_week])
        ).exclude(status='completed').order_by('due_date')

        # Recent activity
        from activity.models import ActivityLog
        context['recent_activities'] = ActivityLog.objects.filter(
            user=user
        ).order_by('-created_at')[:10]

        # Overdue projects
        context['overdue_projects'] = user_projects.filter(
            due_date__lt=today
        ).exclude(status='completed').exclude(status='cancelled')

        return context

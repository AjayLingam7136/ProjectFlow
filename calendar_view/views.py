import calendar
import json
from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))

        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(year, month)

        context['year'] = year
        context['month'] = month
        context['month_name'] = calendar.month_name[month]
        context['month_days'] = month_days
        context['today'] = today
        context['prev_month'] = month - 1 if month > 1 else 12
        context['prev_year'] = year if month > 1 else year - 1
        context['next_month'] = month + 1 if month < 12 else 1
        context['next_year'] = year if month < 12 else year + 1
        context['day_names'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Get events for this month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        user = self.request.user
        from tasks.models import Task
        from projects.models import Project

        tasks = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user),
            due_date__gte=first_day,
            due_date__lte=last_day,
        ).select_related('project', 'assignee').distinct()

        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user),
            due_date__gte=first_day,
            due_date__lte=last_day,
        ).distinct()

        # Build events dict keyed by day
        events = {}
        for task in tasks:
            day = task.due_date.day
            if day not in events:
                events[day] = []
            events[day].append({
                'type': 'task',
                'id': task.pk,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'url': f'/tasks/{task.pk}/',
                'is_overdue': task.is_overdue,
            })

        for project in projects:
            day = project.due_date.day
            if day not in events:
                events[day] = []
            events[day].append({
                'type': 'project',
                'id': project.pk,
                'title': project.name,
                'status': project.status,
                'url': f'/projects/{project.pk}/',
            })

        context['events'] = events
        return context


class CalendarAPIView(LoginRequiredMixin, View):
    """JSON endpoint for calendar events."""

    def get(self, request):
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')

        if not start_str or not end_str:
            return JsonResponse({'events': []})

        try:
            start = date.fromisoformat(start_str)
            end = date.fromisoformat(end_str)
        except ValueError:
            return JsonResponse({'events': []})

        user = request.user
        from tasks.models import Task
        from projects.models import Project

        tasks = Task.objects.filter(
            Q(project__owner=user) | Q(project__team_members=user) | Q(project__memberships__user=user),
            due_date__gte=start,
            due_date__lte=end,
        ).select_related('project', 'assignee').distinct()

        projects = Project.objects.filter(
            Q(owner=user) | Q(team_members=user) | Q(memberships__user=user),
            due_date__gte=start,
            due_date__lte=end,
        ).distinct()

        events = []
        for task in tasks:
            events.append({
                'id': f'task-{task.pk}',
                'type': 'task',
                'title': task.title,
                'date': task.due_date.isoformat(),
                'status': task.status,
                'priority': task.priority,
                'url': f'/tasks/{task.pk}/',
                'is_overdue': task.is_overdue,
            })

        for project in projects:
            events.append({
                'id': f'project-{project.pk}',
                'type': 'project',
                'title': project.name,
                'date': project.due_date.isoformat(),
                'status': project.status,
                'url': f'/projects/{project.pk}/',
            })

        return JsonResponse({'events': events})

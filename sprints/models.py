from django.conf import settings
from django.db import models
from django.utils import timezone

from tasks.models import Task


class Sprint(models.Model):
    """Time-boxed iteration for planning work on a project."""

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='sprints',
    )
    name = models.CharField(max_length=200)
    goal = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['project', 'name']

    def __str__(self):
        return f"{self.name} — {self.project.name}"

    @property
    def total_tasks(self):
        return self.sprint_tasks.count()

    @property
    def completed_tasks(self):
        return self.sprint_tasks.filter(task__status='completed').count()

    @property
    def progress(self):
        total = self.total_tasks
        if total == 0:
            return 0
        return round((self.completed_tasks / total) * 100)

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def is_overdue(self):
        return (
            self.status == 'active'
            and self.end_date
            and timezone.now().date() > self.end_date
        )

    def activate(self):
        """Set this sprint as active; deactivate others in the same project."""
        Sprint.objects.filter(
            project=self.project,
            status='active',
        ).exclude(pk=self.pk).update(status='completed')
        self.status = 'active'
        self.save(update_fields=['status', 'updated_at'])

    def tasks_by_status(self):
        """Return tasks grouped by status."""
        status_order = [status for status, _ in Task.STATUS_CHOICES]
        result = {}
        for status in status_order:
            result[status] = self.sprint_tasks.select_related(
                'task', 'task__assignee', 'task__project'
            ).filter(task__status=status)
        return result


class SprintTask(models.Model):
    """Links a task to a sprint (tasks can appear in multiple sprints historically)."""

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='sprint_tasks',
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='sprint_tasks',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['sprint', 'task']
        ordering = ['added_at']

    def __str__(self):
        return f"{self.task.title} in {self.sprint.name}"

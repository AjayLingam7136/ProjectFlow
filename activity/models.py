from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    """Activity log for tracking user actions across the platform.
    Designed to be extensible for notifications, audit trails, etc."""

    ACTION_CHOICES = [
        ('create_project', 'Created a project'),
        ('update_project', 'Updated a project'),
        ('delete_project', 'Deleted a project'),
        ('create_task', 'Created a task'),
        ('update_task', 'Updated a task'),
        ('delete_task', 'Deleted a task'),
        ('complete_task', 'Completed a task'),
        ('add_comment', 'Added a comment'),
        ('add_team_member', 'Added a team member'),
        ('assign_task', 'Assigned a task'),
        ('change_status', 'Changed task status'),
        ('remove_team_member', 'Removed a team member'),
        ('change_role', 'Changed member role'),
        ('mention_user', 'Mentioned a user'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    message = models.CharField(max_length=500)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user} - {self.action} - {self.created_at}'

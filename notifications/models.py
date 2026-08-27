from django.conf import settings
from django.db import models


class Notification(models.Model):
    """User notification for important events."""

    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_status_changed', 'Task Status Changed'),
        ('task_mentioned', 'Mentioned in Task'),
        ('task_due_soon', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('project_updated', 'Project Updated'),
        ('project_member_added', 'Added to Project'),
        ('comment_added', 'New Comment'),
        ('role_changed', 'Role Changed'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notifications',
    )
    content_type = models.CharField(max_length=50, blank=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.recipient} — {self.title}'


class NotificationPreference(models.Model):
    """Per-user notification preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_prefs',
    )
    task_assigned = models.BooleanField(default=True)
    task_status_changed = models.BooleanField(default=True)
    task_mentioned = models.BooleanField(default=True)
    task_due_soon = models.BooleanField(default=True)
    project_updated = models.BooleanField(default=False)
    comment_added = models.BooleanField(default=True)

    def __str__(self):
        return f'Notification prefs for {self.user}'

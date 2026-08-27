from .models import ActivityLog


def log_activity(user, action, message, obj=None):
    """Centralized activity logging utility.

    Args:
        user: The user performing the action.
        action: One of ActivityLog.ACTION_CHOICES values.
        message: Human-readable description of the action.
        obj: Optional model instance to link (provides pk and class name).
    """
    activity = ActivityLog.objects.create(
        user=user,
        action=action,
        message=message,
        related_object_id=obj.pk if obj else None,
        related_object_type=obj.__class__.__name__ if obj else '',
    )

    # Trigger notification creation
    _create_notifications(activity, obj)

    return activity


def get_activity_for_object(content_type, object_id, limit=50):
    """Get recent activity for a specific object."""
    return ActivityLog.objects.filter(
        related_object_type=content_type,
        related_object_id=object_id,
    ).select_related('user')[:limit]


def _create_notifications(activity, obj):
    """Create notifications based on activity type."""
    from notifications.models import Notification, NotificationPreference

    notification_map = {
        'create_task': ('task_assigned', 'New Task Created'),
        'assign_task': ('task_assigned', 'Task Assigned'),
        'change_status': ('task_status_changed', 'Task Status Changed'),
        'add_comment': ('comment_added', 'New Comment'),
        'add_team_member': ('project_member_added', 'Added to Project'),
        'change_role': ('role_changed', 'Role Changed'),
        'create_issue': ('task_assigned', 'New Issue Created'),
        'assign_issue': ('task_assigned', 'Issue Assigned'),
        'change_issue_status': ('task_status_changed', 'Issue Status Changed'),
    }

    if activity.action not in notification_map:
        return

    notif_type, title = notification_map[activity.action]
    recipients = set()

    if obj is None:
        return

    # Determine recipients based on object type
    obj_type = obj.__class__.__name__

    if obj_type == 'Task':
        if obj.assignee and obj.assignee != activity.user:
            recipients.add(obj.assignee)
        # Notify project owner
        if obj.project.owner != activity.user:
            recipients.add(obj.project.owner)

    elif obj_type == 'Issue':
        if obj.assignee and obj.assignee != activity.user:
            recipients.add(obj.assignee)
        if obj.project.owner != activity.user:
            recipients.add(obj.project.owner)

    elif obj_type == 'Project':
        if activity.action == 'add_team_member':
            # Notify the added member
            pass  # The member is notified through the message
        if obj.owner != activity.user:
            recipients.add(obj.owner)

    # Create notifications for each recipient
    for recipient in recipients:
        # Check notification preferences
        try:
            prefs = NotificationPreference.objects.get(user=recipient)
            pref_field = {
                'task_assigned': 'task_assigned',
                'task_status_changed': 'task_status_changed',
                'add_comment': 'comment_added',
                'add_team_member': 'project_updated',
                'change_role': 'project_updated',
            }.get(activity.action, 'task_assigned')
            if not getattr(prefs, pref_field, True):
                continue
        except NotificationPreference.DoesNotExist:
            pass

        Notification.objects.create(
            recipient=recipient,
            notification_type=notif_type,
            title=title,
            message=activity.message,
            actor=activity.user,
            content_type=obj_type,
            object_id=obj.pk,
        )

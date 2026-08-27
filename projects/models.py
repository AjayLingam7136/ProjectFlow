from django.conf import settings
from django.db import models
from django.utils import timezone


class ProjectMembership(models.Model):
    """Role-based membership linking users to projects."""

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('project_manager', 'Project Manager'),
        ('team_member', 'Team Member'),
        ('viewer', 'Viewer'),
    ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['role']

    def __str__(self):
        return f'{self.user} — {self.get_role_display()} on {self.project}'


class Project(models.Model):
    """Project model with status, priority, team members, and progress tracking."""

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_view_project', 'Can view project'),
            ('can_edit_project', 'Can edit project'),
            ('can_delete_project', 'Can delete project'),
        ]

    def __str__(self):
        return self.name

    @property
    def progress(self):
        """Calculate progress percentage based on task completion."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed = self.tasks.filter(status='completed').count()
        return round((completed / total_tasks) * 100)

    @property
    def completed_tasks_count(self):
        return self.tasks.filter(status='completed').count()

    @property
    def is_overdue(self):
        """Check if project is overdue (not completed and past due date)."""
        if self.due_date and self.status != 'completed' and timezone.now().date() > self.due_date:
            return True
        return False

    def get_team_avatars(self):
        """Return list of team members with avatars (limited to 5)."""
        return list(self.team_members.all()[:5])

    def get_remaining_members(self):
        """Return count of team members beyond the first 5."""
        return max(0, self.team_members.count() - 5)

    def get_user_role(self, user):
        """Return the user's role in this project, or None."""
        if user == self.owner:
            return 'admin'
        try:
            membership = self.memberships.get(user=user)
            return membership.role
        except ProjectMembership.DoesNotExist:
            if user in self.team_members.all():
                return 'team_member'
            return None

    def user_can_edit(self, user):
        """Check if user can edit the project."""
        if user == self.owner or user.is_superuser:
            return True
        role = self.get_user_role(user)
        return role in ('admin', 'project_manager')

    def user_can_delete(self, user):
        """Check if user can delete the project."""
        if user == self.owner or user.is_superuser:
            return True
        role = self.get_user_role(user)
        return role == 'admin'

    def user_can_manage_tasks(self, user):
        """Check if user can create/edit tasks."""
        if user == self.owner or user.is_superuser:
            return True
        role = self.get_user_role(user)
        return role in ('admin', 'project_manager', 'team_member')

    def user_is_member(self, user):
        """Check if user has any access to this project."""
        if user == self.owner or user.is_superuser:
            return True
        return self.get_user_role(user) is not None


class ProjectBookmark(models.Model):
    """Bookmark/star a project for quick access."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_projects',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'project']

    def __str__(self):
        return f'{self.user} bookmarked {self.project}'

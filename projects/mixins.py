from django.contrib.auth.mixins import UserPassesTestMixin

from .models import ProjectMembership


class ProjectPermissionMixin(UserPassesTestMixin):
    """Centralized permission check using ProjectMembership roles.

    Subclasses set `required_roles` to a list of allowed roles.
    If None, any project member (including owner) passes.
    """

    required_roles = None

    def get_project(self):
        if hasattr(self, 'object') and self.object:
            return self.object
        return None

    def test_func(self):
        project = self.get_project()
        if project is None:
            try:
                project = self.get_object()
            except Exception:
                return False

        user = self.request.user
        if user.is_superuser:
            return True
        if project.owner == user:
            return True

        role = project.get_user_role(user)
        if role is None:
            return False
        if self.required_roles is None:
            return True
        return role in self.required_roles


class ProjectOwnerOrAdminMixin(ProjectPermissionMixin):
    """Only project owner or admin role can access."""
    required_roles = ['admin']


class ProjectManagerMixin(ProjectPermissionMixin):
    """Project manager or above can access."""
    required_roles = ['admin', 'project_manager']


class ProjectTeamMixin(ProjectPermissionMixin):
    """Any team member or above can access."""
    required_roles = ['admin', 'project_manager', 'team_member']

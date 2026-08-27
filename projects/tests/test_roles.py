from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project, ProjectMembership

User = get_user_model()


class ProjectMembershipModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@test.com', username='user2', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)

    def test_owner_role(self):
        self.assertEqual(self.project.get_user_role(self.owner), 'admin')

    def test_member_role(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='team_member')
        self.assertEqual(self.project.get_user_role(self.user1), 'team_member')

    def test_non_member_role(self):
        self.assertIsNone(self.project.get_user_role(self.user2))

    def test_user_can_edit_owner(self):
        self.assertTrue(self.project.user_can_edit(self.owner))

    def test_user_can_edit_team_member(self):
        self.assertFalse(self.project.user_can_edit(self.user1))

    def test_user_can_edit_project_manager(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='project_manager')
        self.assertTrue(self.project.user_can_edit(self.user1))

    def test_user_can_delete_owner(self):
        self.assertTrue(self.project.user_can_delete(self.owner))

    def test_user_can_delete_admin_member(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='admin')
        self.assertTrue(self.project.user_can_delete(self.user1))

    def test_user_can_delete_project_manager(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='project_manager')
        self.assertFalse(self.project.user_can_delete(self.user1))

    def test_user_can_manage_tasks_member(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='team_member')
        self.assertTrue(self.project.user_can_manage_tasks(self.user1))

    def test_user_can_manage_tasks_viewer(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='viewer')
        self.assertFalse(self.project.user_can_manage_tasks(self.user1))

    def test_user_is_member(self):
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='viewer')
        self.assertTrue(self.project.user_is_member(self.user1))

    def test_user_is_not_member(self):
        self.assertFalse(self.project.user_is_member(self.user2))


class ProjectMembersViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@test.com', username='user2', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='team_member')

    def test_members_view_requires_login(self):
        response = self.client.get(reverse('projects:members', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_view_members(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(reverse('projects:members', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)

    def test_member_can_view_members(self):
        self.client.login(email='user1@test.com', password='testpass123')
        response = self.client.get(reverse('projects:members', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)

    def test_non_member_cannot_view(self):
        self.client.login(email='user2@test.com', password='testpass123')
        response = self.client.get(reverse('projects:members', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 403)

    def test_add_member(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.post(reverse('projects:member_add', kwargs={'pk': self.project.pk}), {
            'user': self.user2.pk,
            'role': 'team_member',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProjectMembership.objects.filter(project=self.project, user=self.user2).exists())

    def test_change_role(self):
        membership = ProjectMembership.objects.get(project=self.project, user=self.user1)
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.post(reverse('projects:member_role', kwargs={'pk': self.project.pk, 'member_id': membership.pk}), {
            'role': 'project_manager',
        })
        self.assertEqual(response.status_code, 302)
        membership.refresh_from_db()
        self.assertEqual(membership.role, 'project_manager')

    def test_remove_member(self):
        membership = ProjectMembership.objects.get(project=self.project, user=self.user1)
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.post(reverse('projects:member_remove', kwargs={'pk': self.project.pk, 'member_id': membership.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ProjectMembership.objects.filter(project=self.project, user=self.user1).exists())

    def test_viewer_cannot_add_member(self):
        ProjectMembership.objects.create(project=self.project, user=self.user2, role='viewer')
        self.client.login(email='user2@test.com', password='testpass123')
        new_user = User.objects.create_user(email='new@test.com', username='new', password='testpass123')
        response = self.client.post(reverse('projects:member_add', kwargs={'pk': self.project.pk}), {
            'user': new_user.pk,
            'role': 'team_member',
        })
        self.assertEqual(response.status_code, 403)

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            status='in_progress',
            priority='high',
            start_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            owner=self.user,
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), 'Test Project')

    def test_project_progress_no_tasks(self):
        self.assertEqual(self.project.progress, 0)

    def test_project_is_overdue_false(self):
        self.assertFalse(self.project.is_overdue)

    def test_project_is_overdue_true(self):
        self.project.due_date = date.today() - timedelta(days=1)
        self.project.save()
        self.assertTrue(self.project.is_overdue)


class ProjectViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='other@example.com', password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            status='in_progress',
            priority='high',
            owner=self.user,
        )

    def test_project_list_requires_login(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 302)

    def test_project_list_when_logged_in(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_detail_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('projects:detail', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_create_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('projects:create'), {
            'name': 'New Project',
            'description': 'New description',
            'status': 'planning',
            'priority': 'medium',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_project_update_only_owner(self):
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.post(reverse('projects:edit', kwargs={'pk': self.project.pk}), {
            'name': 'Hacked',
        })
        self.assertEqual(response.status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Test Project')

    def test_project_delete_only_owner(self):
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.post(reverse('projects:delete', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())


class ProjectFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )

    def test_valid_project_form(self):
        from .forms import ProjectForm
        form = ProjectForm(data={
            'name': 'Test',
            'description': 'Desc',
            'status': 'planning',
            'priority': 'medium',
            'start_date': date.today(),
            'due_date': date.today() + timedelta(days=5),
        })
        self.assertTrue(form.is_valid())

    def test_invalid_due_before_start(self):
        from .forms import ProjectForm
        form = ProjectForm(data={
            'name': 'Test',
            'description': 'Desc',
            'status': 'planning',
            'priority': 'medium',
            'start_date': date.today() + timedelta(days=10),
            'due_date': date.today(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

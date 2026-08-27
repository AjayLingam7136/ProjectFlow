import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from projects.models import Project, ProjectMembership
from tasks.models import Task, Tag

User = get_user_model()


class TaskModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            created_by=self.owner,
            order=0,
            estimated_hours=5.0,
        )

    def test_order_field(self):
        self.assertEqual(self.task.order, 0)
        self.task.order = 5
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.order, 5)

    def test_estimated_hours(self):
        self.assertEqual(self.task.estimated_hours, 5.0)

    def test_estimated_hours_nullable(self):
        task = Task.objects.create(
            title='No Hours',
            project=self.project,
            created_by=self.owner,
        )
        self.assertIsNone(task.estimated_hours)


class TaskBulkStatusUpdateViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.task1 = Task.objects.create(title='Task 1', project=self.project, created_by=self.owner, status='todo')
        self.task2 = Task.objects.create(title='Task 2', project=self.project, created_by=self.owner, status='todo')
        self.client = Client()

    def test_bulk_update_requires_login(self):
        response = self.client.post(reverse('tasks:bulk_status'), json.dumps({'task_ids': [self.task1.pk], 'status': 'in_progress'}), content_type='application/json')
        self.assertEqual(response.status_code, 302)

    def test_bulk_update(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.post(
            reverse('tasks:bulk_status'),
            json.dumps({'task_ids': [self.task1.pk, self.task2.pk], 'status': 'in_progress'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['updated'], 2)
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertEqual(self.task1.status, 'in_progress')
        self.assertEqual(self.task2.status, 'in_progress')

    def test_bulk_update_invalid_status(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.post(
            reverse('tasks:bulk_status'),
            json.dumps({'task_ids': [self.task1.pk], 'status': 'invalid'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class TaskReorderViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.task1 = Task.objects.create(title='Task 1', project=self.project, created_by=self.owner, order=0)
        self.task2 = Task.objects.create(title='Task 2', project=self.project, created_by=self.owner, order=1)
        self.client = Client()

    def test_reorder(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.post(
            reverse('tasks:reorder'),
            json.dumps({'orders': [{'id': self.task1.pk, 'order': 5}, {'id': self.task2.pk, 'order': 3}]}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertEqual(self.task1.order, 5)
        self.assertEqual(self.task2.order, 3)


class TaskAPIViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.tag = Tag.objects.create(name='urgent', color='#ef4444')
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            created_by=self.owner,
            status='todo',
            priority='high',
            order=2,
        )
        self.task.tags.add(self.tag)
        self.client = Client()

    def test_api_requires_login(self):
        response = self.client.get(reverse('tasks:api_tasks'))
        self.assertEqual(response.status_code, 302)

    def test_api_returns_tasks(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(reverse('tasks:api_tasks'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['tasks']), 1)
        task_data = data['tasks'][0]
        self.assertEqual(task_data['id'], self.task.pk)
        self.assertEqual(task_data['title'], 'Test Task')
        self.assertEqual(task_data['status'], 'todo')
        self.assertEqual(task_data['priority'], 'high')
        self.assertEqual(task_data['order'], 2)
        self.assertEqual(len(task_data['tags']), 1)

    def test_api_filter_by_project(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(f'{reverse("tasks:api_tasks")}?project={self.project.pk}')
        data = json.loads(response.content)
        self.assertEqual(len(data['tasks']), 1)

    def test_api_filter_by_status(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(f'{reverse("tasks:api_tasks")}?status=completed')
        data = json.loads(response.content)
        self.assertEqual(len(data['tasks']), 0)


class TaskFilterFormTest(TestCase):
    def test_tag_filter(self):
        from tasks.forms import TaskFilterForm
        form = TaskFilterForm({'tag': ''})
        self.assertTrue(form.is_valid())

    def test_date_range_filter(self):
        from tasks.forms import TaskFilterForm
        form = TaskFilterForm({'due_before': '2025-12-31', 'due_after': '2025-01-01'})
        self.assertTrue(form.is_valid())

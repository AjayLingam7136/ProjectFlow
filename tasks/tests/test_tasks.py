from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from tasks.models import Comment, Tag, Task

User = get_user_model()


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user,
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='A test task',
            project=self.project,
            assignee=self.user,
            status='in_progress',
            priority='high',
            due_date=date.today() + timedelta(days=5),
            created_by=self.user,
        )

    def test_task_str(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_is_overdue_false(self):
        self.assertFalse(self.task.is_overdue)

    def test_task_is_overdue_true(self):
        self.task.due_date = date.today() - timedelta(days=1)
        self.task.save()
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_overdue)

    def test_task_progress_on_project(self):
        """Project progress should reflect task completion."""
        self.assertEqual(self.project.progress, 0)
        self.task.status = 'completed'
        self.task.save()
        self.assertEqual(self.project.progress, 100)

    def test_tag_str(self):
        tag = Tag.objects.create(name='Frontend', color='#3b82f6')
        self.assertEqual(str(tag), 'Frontend')

    def test_comment_str(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,
            body='Test comment',
        )
        self.assertIn('Comment by', str(comment))


class TaskViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user,
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='A test task',
            project=self.project,
            assignee=self.user,
            status='in_progress',
            priority='high',
            created_by=self.user,
        )

    def test_task_list_requires_login(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 302)

    def test_task_list_when_logged_in(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_detail_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('tasks:detail', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_create_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('tasks:create'), {
            'title': 'New Task',
            'description': 'New desc',
            'project': self.project.pk,
            'assignee': self.user.pk,
            'status': 'todo',
            'priority': 'medium',
            'due_date': date.today() + timedelta(days=7),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_task_status_update(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('tasks:status', kwargs={'pk': self.task.pk}), {
            'status': 'completed',
        })
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_comment_create(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('tasks:comment', kwargs={'pk': self.task.pk}), {
            'body': 'This is a test comment.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(body='This is a test comment.').exists())

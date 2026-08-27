import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from activity.models import ActivityLog
from activity.utils import get_activity_for_object, log_activity
from projects.models import Project, ProjectMembership
from tasks.models import Comment, Task

User = get_user_model()


class LogActivityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', username='user', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.user)

    def test_log_activity_basic(self):
        activity = log_activity(self.user, 'create_project', 'Created project', self.project)
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.action, 'create_project')
        self.assertEqual(activity.message, 'Created project')
        self.assertEqual(activity.related_object_id, self.project.pk)
        self.assertEqual(activity.related_object_type, 'Project')

    def test_log_activity_no_object(self):
        activity = log_activity(self.user, 'create_task', 'Created a task')
        self.assertIsNone(activity.related_object_id)
        self.assertEqual(activity.related_object_type, '')

    def test_get_activity_for_object(self):
        log_activity(self.user, 'create_project', 'Created project', self.project)
        log_activity(self.user, 'update_project', 'Updated project', self.project)
        activities = get_activity_for_object('Project', self.project.pk)
        self.assertEqual(activities.count(), 2)


class ActivityLogExtendedChoicesTest(TestCase):
    def test_new_choices_exist(self):
        choices = dict(ActivityLog.ACTION_CHOICES)
        self.assertIn('assign_task', choices)
        self.assertIn('change_status', choices)
        self.assertIn('remove_team_member', choices)
        self.assertIn('change_role', choices)
        self.assertIn('mention_user', choices)


class ActivityLogByObjectViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.task = Task.objects.create(title='Test Task', project=self.project, created_by=self.owner)
        log_activity(self.owner, 'create_task', f'Created task "{self.task.title}"', self.task)
        self.client = Client()

    def test_requires_login(self):
        response = self.client.get(reverse('activity:by_object', kwargs={'content_type': 'Task', 'object_id': self.task.pk}))
        self.assertEqual(response.status_code, 302)

    def test_returns_activity(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(reverse('activity:by_object', kwargs={'content_type': 'Task', 'object_id': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['activities']), 1)


class CommentEditDeleteTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.user1 = User.objects.create_user(email='user1@test.com', username='user1', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.task = Task.objects.create(title='Test Task', project=self.project, created_by=self.owner)
        self.comment = Comment.objects.create(task=self.task, author=self.user1, body='Test comment')
        self.client = Client()

    def test_author_can_edit(self):
        self.client.login(email='user1@test.com', password='testpass123')
        response = self.client.get(reverse('tasks:comment_edit', kwargs={'pk': self.task.pk, 'comment_id': self.comment.pk}))
        self.assertEqual(response.status_code, 200)

    def test_non_author_cannot_edit(self):
        other_user = User.objects.create_user(email='other@test.com', username='other', password='testpass123')
        self.client.login(email='other@test.com', password='testpass123')
        response = self.client.get(reverse('tasks:comment_edit', kwargs={'pk': self.task.pk, 'comment_id': self.comment.pk}))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit_any_comment(self):
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(reverse('tasks:comment_edit', kwargs={'pk': self.task.pk, 'comment_id': self.comment.pk}))
        self.assertEqual(response.status_code, 200)

    def test_edit_comment_sets_edited_at(self):
        self.client.login(email='user1@test.com', password='testpass123')
        response = self.client.post(
            reverse('tasks:comment_edit', kwargs={'pk': self.task.pk, 'comment_id': self.comment.pk}),
            {'body': 'Updated comment'}
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertIsNotNone(self.comment.edited_at)

    def test_author_can_delete(self):
        self.client.login(email='user1@test.com', password='testpass123')
        response = self.client.post(reverse('tasks:comment_delete', kwargs={'pk': self.task.pk, 'comment_id': self.comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


class TaskActivityLoggingTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', username='owner', password='testpass123')
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.client = Client()

    def test_create_task_logs_activity(self):
        self.client.login(email='owner@test.com', password='testpass123')
        self.client.post(reverse('tasks:create'), {
            'title': 'New Task',
            'project': self.project.pk,
            'status': 'todo',
            'priority': 'medium',
        })
        activity = ActivityLog.objects.filter(action='create_task').first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.user, self.owner)

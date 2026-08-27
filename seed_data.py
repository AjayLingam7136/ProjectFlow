"""
Seed script for demo data.
Run: python manage.py shell -c "from seed_data import run; run()"
Or:  python manage.py shell < seed_data.py
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from projects.models import Project
from tasks.models import Comment, Tag, Task

User = get_user_model()


def run():
    with transaction.atomic():
        # Create demo users
        users_data = [
            {'username': 'alice', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Anderson', 'password': 'demo123'},
            {'username': 'bob', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Brown', 'password': 'demo123'},
            {'username': 'charlie', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Clark', 'password': 'demo123'},
        ]

        users = {}
        for ud in users_data:
            user, created = User.objects.get_or_create(
                username=ud['username'],
                defaults={
                    'email': ud['email'],
                    'first_name': ud['first_name'],
                    'last_name': ud['last_name'],
                }
            )
            if created:
                user.set_password(ud['password'])
                user.save()
            users[ud['username']] = user

        # Create tags
        tags_data = [
            {'name': 'Frontend', 'color': '#3b82f6'},
            {'name': 'Backend', 'color': '#10b981'},
            {'name': 'Design', 'color': '#8b5cf6'},
            {'name': 'Bug', 'color': '#ef4444'},
            {'name': 'Feature', 'color': '#f59e0b'},
        ]
        tags = {}
        for td in tags_data:
            tag, _ = Tag.objects.get_or_create(name=td['name'], defaults={'color': td['color']})
            tags[td['name']] = tag

        today = timezone.now().date()

        # Create projects
        projects_data = [
            {
                'name': 'E-Commerce Redesign',
                'description': 'Complete redesign of the e-commerce platform with modern UI/UX and improved performance.',
                'status': 'in_progress',
                'priority': 'high',
                'start_date': today,
                'due_date': today + timedelta(days=15),
                'owner': users['alice'],
                'team': [users['bob'], users['charlie']],
            },
            {
                'name': 'Mobile App Development',
                'description': 'Building a cross-platform mobile app for iOS and Android using React Native.',
                'status': 'in_progress',
                'priority': 'critical',
                'start_date': today,
                'due_date': today + timedelta(days=30),
                'owner': users['bob'],
                'team': [users['alice'], users['charlie']],
            },
            {
                'name': 'API Migration',
                'description': 'Migrate legacy REST API to GraphQL with improved schema and documentation.',
                'status': 'planning',
                'priority': 'medium',
                'start_date': today,
                'due_date': today + timedelta(days=45),
                'owner': users['alice'],
                'team': [users['charlie']],
            },
            {
                'name': 'Q3 Marketing Campaign',
                'description': 'Plan and execute the Q3 marketing campaign including social media and email outreach.',
                'status': 'planning',
                'priority': 'low',
                'start_date': today,
                'due_date': today + timedelta(days=60),
                'owner': users['charlie'],
                'team': [users['alice'], users['bob']],
            },
        ]

        projects = []
        for pd in projects_data:
            project, created = Project.objects.get_or_create(
                name=pd['name'],
                defaults={
                    'description': pd['description'],
                    'status': pd['status'],
                    'priority': pd['priority'],
                    'start_date': pd['start_date'],
                    'due_date': pd['due_date'],
                    'owner': pd['owner'],
                }
            )
            if created:
                project.team_members.set(pd['team'])
            projects.append(project)

        # Create tasks
        tasks_data = [
            {
                'title': 'Design Homepage Mockups',
                'description': 'Create high-fidelity mockups for the homepage with focus on conversion optimization.',
                'project': projects[0],
                'assignee': users['alice'],
                'status': 'completed',
                'priority': 'high',
                'due_date': today - timedelta(days=5),
                'tags': [tags['Design']],
                'created_by': users['alice'],
            },
            {
                'title': 'Setup Product Database Schema',
                'description': 'Design and implement the database schema for product catalog with proper indexing.',
                'project': projects[0],
                'assignee': users['bob'],
                'status': 'completed',
                'priority': 'critical',
                'due_date': today - timedelta(days=3),
                'tags': [tags['Backend'], tags['Feature']],
                'created_by': users['bob'],
            },
            {
                'title': 'Implement Cart Functionality',
                'description': 'Build shopping cart with add/remove items, quantity adjustment, and persistence.',
                'project': projects[0],
                'assignee': users['bob'],
                'status': 'in_progress',
                'priority': 'high',
                'due_date': today + timedelta(days=2),
                'tags': [tags['Backend'], tags['Feature']],
                'created_by': users['alice'],
            },
            {
                'title': 'Create Checkout Flow',
                'description': 'Design and implement the checkout process with payment integration.',
                'project': projects[0],
                'assignee': users['charlie'],
                'status': 'todo',
                'priority': 'critical',
                'due_date': today + timedelta(days=5),
                'tags': [tags['Frontend'], tags['Feature']],
                'created_by': users['alice'],
            },
            {
                'title': 'Set Up CI/CD Pipeline',
                'description': 'Configure continuous integration and deployment for the mobile app.',
                'project': projects[1],
                'assignee': users['charlie'],
                'status': 'in_progress',
                'priority': 'high',
                'due_date': today + timedelta(days=1),
                'tags': [tags['Backend'], tags['Feature']],
                'created_by': users['bob'],
            },
            {
                'title': 'Fix Login Screen Bug',
                'description': 'Resolve the issue where the login screen crashes on iOS devices.',
                'project': projects[1],
                'assignee': users['alice'],
                'status': 'completed',
                'priority': 'critical',
                'due_date': today - timedelta(days=2),
                'tags': [tags['Bug']],
                'created_by': users['bob'],
            },
            {
                'title': 'Write API Documentation',
                'description': 'Document the GraphQL API endpoints with examples and schema reference.',
                'project': projects[2],
                'assignee': users['charlie'],
                'status': 'todo',
                'priority': 'medium',
                'due_date': today + timedelta(days=10),
                'tags': [tags['Backend'], tags['Feature']],
                'created_by': users['alice'],
            },
            {
                'title': 'Create Landing Page',
                'description': 'Build the marketing landing page for the Q3 campaign.',
                'project': projects[3],
                'assignee': users['alice'],
                'status': 'todo',
                'priority': 'medium',
                'due_date': today + timedelta(days=20),
                'tags': [tags['Frontend'], tags['Design']],
                'created_by': users['charlie'],
            },
            {
                'title': 'Plan Social Media Content',
                'description': 'Outline content calendar for LinkedIn, Twitter, and Instagram posts.',
                'project': projects[3],
                'assignee': users['bob'],
                'status': 'in_progress',
                'priority': 'low',
                'due_date': today + timedelta(days=3),
                'tags': [tags['Design']],
                'created_by': users['charlie'],
            },
        ]

        for td in tasks_data:
            task, created = Task.objects.get_or_create(
                title=td['title'],
                defaults={
                    'description': td['description'],
                    'project': td['project'],
                    'assignee': td['assignee'],
                    'status': td['status'],
                    'priority': td['priority'],
                    'due_date': td['due_date'],
                    'created_by': td['created_by'],
                }
            )
            if created:
                task.tags.set(td['tags'])

        # Create comments
        task1 = Task.objects.get(title='Implement Cart Functionality')
        Comment.objects.get_or_create(
            task=task1,
            author=users['bob'],
            defaults={'body': 'Started working on the cart implementation. Database schema is ready.'},
        )
        Comment.objects.get_or_create(
            task=task1,
            author=users['alice'],
            defaults={'body': 'Good progress! Let me know if you need any design assets.'},
        )

        task2 = Task.objects.get(title='Set Up CI/CD Pipeline')
        Comment.objects.get_or_create(
            task=task2,
            author=users['charlie'],
            defaults={'body': 'Pipeline is almost ready. Just need to configure the Android build step.'},
        )

        print('Seed data created successfully!')
        print(f'  Users: {User.objects.count()}')
        print(f'  Projects: {Project.objects.count()}')
        print(f'  Tasks: {Task.objects.count()}')
        print(f'  Tags: {Tag.objects.count()}')
        print(f'  Comments: {Comment.objects.count()}')


if __name__ == '__main__':
    run()

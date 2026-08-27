from django.db import migrations


def populate_memberships(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    ProjectMembership = apps.get_model('projects', 'ProjectMembership')

    for project in Project.objects.all():
        # Create admin membership for the owner
        ProjectMembership.objects.get_or_create(
            project=project,
            user=project.owner,
            defaults={'role': 'admin'},
        )
        # Create team_member memberships for existing team members
        for member in project.team_members.all():
            ProjectMembership.objects.get_or_create(
                project=project,
                user=member,
                defaults={'role': 'team_member'},
            )


def reverse_populate(apps, schema_editor):
    ProjectMembership = apps.get_model('projects', 'ProjectMembership')
    ProjectMembership.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_projectmembership'),
    ]

    operations = [
        migrations.RunPython(populate_memberships, reverse_populate),
    ]

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import F


def backfill_assigned_by(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    Task.objects.filter(assignee__isnull=False).update(assigned_by=F('created_by'))


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_theme_preference'),
        ('tasks', '0003_comment_edited_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='assigned_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_tasks_by',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_assigned_by, migrations.RunPython.noop),
    ]

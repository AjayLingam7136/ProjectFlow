from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import F


def backfill_assigned_by(apps, schema_editor):
    Issue = apps.get_model('issues', 'Issue')
    Issue.objects.filter(assignee__isnull=False).update(assigned_by=F('created_by'))


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_theme_preference'),
        ('issues', '0002_alter_issue_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='assigned_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_issues_by',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_assigned_by, migrations.RunPython.noop),
    ]

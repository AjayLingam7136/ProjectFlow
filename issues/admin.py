from django.contrib import admin
from .models import Issue, IssueComment


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'severity', 'assignee', 'due_date']
    list_filter = ['status', 'priority', 'severity']
    search_fields = ['title', 'description']


@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ['issue', 'author', 'created_at']

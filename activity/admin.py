from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'message', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('message', 'user__email', 'user__username')
    readonly_fields = ('user', 'action', 'message', 'related_object_id', 'related_object_type', 'created_at')

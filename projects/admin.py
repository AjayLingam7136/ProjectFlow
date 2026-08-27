from django.contrib import admin

from .models import Project, ProjectMembership


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__email', 'user__username', 'project__name')
    readonly_fields = ('joined_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'priority', 'owner', 'start_date', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('status', 'priority')
    filter_horizontal = ('team_members',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'owner')}),
        ('Details', {'fields': ('status', 'priority', 'start_date', 'due_date')}),
        ('Team', {'fields': ('team_members',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

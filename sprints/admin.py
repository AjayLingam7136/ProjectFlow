from django.contrib import admin

from .models import Sprint, SprintTask


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'project', 'created_at')
    search_fields = ('name', 'goal')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('project', 'name', 'goal')}),
        ('Dates', {'fields': ('start_date', 'end_date')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(SprintTask)
class SprintTaskAdmin(admin.ModelAdmin):
    list_display = ('sprint', 'task', 'added_at')
    list_filter = ('sprint__status',)
    search_fields = ('task__title',)
    readonly_fields = ('added_at',)

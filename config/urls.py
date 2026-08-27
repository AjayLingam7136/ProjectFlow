"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth (no prefix)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Apps
    path('', include('core.urls')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('activity/', include('activity.urls', namespace='activity')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('calendar/', include('calendar_view.urls', namespace='calendar_view')),
    path('sprints/', include('sprints.urls', namespace='sprints')),
    path('issues/', include('issues.urls', namespace='issues')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = core_views.page_not_found
handler500 = core_views.server_error

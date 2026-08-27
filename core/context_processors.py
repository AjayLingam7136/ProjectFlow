from django.conf import settings


def global_settings(request):
    return {
        'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', 'ProjectFlow'),
    }

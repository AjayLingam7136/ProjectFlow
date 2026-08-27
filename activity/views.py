from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from .models import ActivityLog
from .utils import get_activity_for_object


class ActivityLogListView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'activity/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 30

    def get_queryset(self):
        qs = ActivityLog.objects.filter(user=self.request.user).select_related('user')
        action = self.request.GET.get('action')
        if action:
            qs = qs.filter(action=action)
        return qs


class ActivityLogByObjectView(LoginRequiredMixin, View):
    """Return activity for a specific project or task."""

    def get(self, request, content_type, object_id):
        activities = get_activity_for_object(content_type, object_id)
        data = []
        for a in activities:
            data.append({
                'id': a.pk,
                'user': a.user.get_full_name() or a.user.username,
                'user_initials': a.user.get_initials,
                'action': a.get_action_display(),
                'message': a.message,
                'created_at': a.created_at.isoformat(),
            })
        return JsonResponse({'activities': data})

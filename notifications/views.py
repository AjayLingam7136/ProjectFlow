from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from .models import Notification, NotificationPreference


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 30

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user)
        filter_type = self.request.GET.get('filter')
        if filter_type == 'unread':
            qs = qs.filter(is_read=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user, is_read=False
        ).count()
        context['current_filter'] = self.request.GET.get('filter', '')
        return context


class NotificationUnreadCountView(LoginRequiredMixin, View):
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'unread_count': count})


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return JsonResponse({'success': True, 'updated': updated})


class NotificationPreferenceUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        return JsonResponse({
            'task_assigned': prefs.task_assigned,
            'task_status_changed': prefs.task_status_changed,
            'task_mentioned': prefs.task_mentioned,
            'task_due_soon': prefs.task_due_soon,
            'project_updated': prefs.project_updated,
            'comment_added': prefs.comment_added,
        })

    def post(self, request):
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False}, status=400)

        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        for field in ['task_assigned', 'task_status_changed', 'task_mentioned', 'task_due_soon', 'project_updated', 'comment_added']:
            if field in data:
                setattr(prefs, field, data[field])
        prefs.save()
        return JsonResponse({'success': True})

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('unread-count/', views.NotificationUnreadCountView.as_view(), name='unread_count'),
    path('<int:pk>/read/', views.NotificationMarkReadView.as_view(), name='mark_read'),
    path('read-all/', views.NotificationMarkAllReadView.as_view(), name='mark_all_read'),
    path('preferences/', views.NotificationPreferenceUpdateView.as_view(), name='preferences'),
]

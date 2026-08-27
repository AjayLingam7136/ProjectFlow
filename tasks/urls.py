from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:pk>/status/', views.TaskStatusUpdateView.as_view(), name='status'),
    path('<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment'),
    path('<int:pk>/comment/<int:comment_id>/edit/', views.CommentEditView.as_view(), name='comment_edit'),
    path('<int:pk>/comment/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('bulk-status/', views.TaskBulkStatusUpdateView.as_view(), name='bulk_status'),
    path('reorder/', views.TaskReorderView.as_view(), name='reorder'),
    path('api/', views.TaskAPIView.as_view(), name='api_tasks'),
    path('kanban/', views.KanbanBoardView.as_view(), name='kanban'),
    path('kanban/move/', views.KanbanTaskMoveView.as_view(), name='kanban_move'),
]

from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('', views.IssueListView.as_view(), name='list'),
    path('create/', views.IssueCreateView.as_view(), name='create'),
    path('<int:pk>/', views.IssueDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.IssueUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.IssueDeleteView.as_view(), name='delete'),
    path('<int:pk>/status/', views.IssueStatusUpdateView.as_view(), name='status'),
    path('<int:pk>/resolution/', views.IssueResolutionUpdateView.as_view(), name='resolution'),
    path('<int:pk>/comment/', views.IssueCommentCreateView.as_view(), name='comment'),
    path('<int:pk>/comment/<int:comment_id>/edit/', views.IssueCommentEditView.as_view(), name='comment_edit'),
    path('<int:pk>/comment/<int:comment_id>/delete/', views.IssueCommentDeleteView.as_view(), name='comment_delete'),
    path('bulk-status/', views.IssueBulkStatusUpdateView.as_view(), name='bulk_status'),
    path('api/', views.IssueAPIView.as_view(), name='api_issues'),
    path('kanban/move/', views.IssueKanbanMoveView.as_view(), name='kanban_move'),
]

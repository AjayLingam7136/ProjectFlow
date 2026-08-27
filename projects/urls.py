from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    path('<int:pk>/members/', views.ProjectMembersView.as_view(), name='members'),
    path('<int:pk>/members/add/', views.ProjectMemberAddView.as_view(), name='member_add'),
    path('<int:pk>/members/<int:member_id>/role/', views.ProjectMemberRoleUpdateView.as_view(), name='member_role'),
    path('<int:pk>/members/<int:member_id>/remove/', views.ProjectMemberRemoveView.as_view(), name='member_remove'),
    path('<int:pk>/bookmark/', views.ProjectBookmarkToggleView.as_view(), name='bookmark'),
]

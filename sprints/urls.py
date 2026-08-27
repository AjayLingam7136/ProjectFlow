from django.urls import path

from . import views

app_name = 'sprints'

urlpatterns = [
    path('', views.SprintListView.as_view(), name='list'),
    path('create/', views.SprintCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SprintDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SprintUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.SprintDeleteView.as_view(), name='delete'),
    path('<int:pk>/add-task/', views.AddTaskToSprintView.as_view(), name='add_task'),
    path('<int:pk>/remove-task/<int:task_pk>/', views.RemoveTaskFromSprintView.as_view(), name='remove_task'),
]

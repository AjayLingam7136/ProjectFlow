from django.urls import path
from . import views

app_name = 'activity'

urlpatterns = [
    path('', views.ActivityLogListView.as_view(), name='list'),
    path('object/<str:content_type>/<int:object_id>/', views.ActivityLogByObjectView.as_view(), name='by_object'),
]

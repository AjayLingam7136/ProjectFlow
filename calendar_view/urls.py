from django.urls import path
from . import views

app_name = 'calendar_view'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='month'),
    path('api/events/', views.CalendarAPIView.as_view(), name='api_events'),
]

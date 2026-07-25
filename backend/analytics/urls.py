# analytics/urls.py

from django.urls import path
from .views import DashboardStatsView, ProjectAnalyticsView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('projects/',  ProjectAnalyticsView.as_view(), name='project_analytics'),
]
# projects/urls.py

from django.urls import path
from .views import (
    ProjectListView,
    ProjectDetailView,
    AssignArchitectView,
    MilestoneListView,
    MilestoneDetailView,
)

urlpatterns = [
    path('',
         ProjectListView.as_view(),
         name='project_list'),

    path('<int:pk>/',
         ProjectDetailView.as_view(),
         name='project_detail'),

    path('<int:pk>/assign/',
         AssignArchitectView.as_view(),
         name='assign_architect'),

    path('<int:project_id>/milestones/',
         MilestoneListView.as_view(),
         name='milestone_list'),

    path('milestones/<int:pk>/',
         MilestoneDetailView.as_view(),
         name='milestone_detail'),
]
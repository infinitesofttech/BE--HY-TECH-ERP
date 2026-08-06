from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('analytics/', views.ProjectAnalyticsView.as_view(), name='project-analytics'),
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('todos/', views.TodoItemListCreateView.as_view(), name='todo-list'),
    path('todos/<int:pk>/', views.TodoItemDetailView.as_view(), name='todo-detail'),
    path('timesheets/', views.TimesheetListCreateView.as_view(), name='timesheet-list'),
    path('timesheets/<int:pk>/', views.TimesheetDetailView.as_view(), name='timesheet-detail'),
    path('milestones/', views.MilestoneListCreateView.as_view(), name='milestone-list'),
    path('milestones/<int:pk>/', views.MilestoneDetailView.as_view(), name='milestone-detail'),
    path('resource-allocations/', views.ResourceAllocationListCreateView.as_view(), name='resource-allocation-list'),
    path('resource-allocations/<int:pk>/', views.ResourceAllocationDetailView.as_view(), name='resource-allocation-detail'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('teams/', views.TeamListCreateView.as_view(), name='team-list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team-detail'),
    path('assign/', views.TargetAssignView.as_view(), name='target-assign'),
    path('', views.TargetListView.as_view(), name='target-list'),
    path('my/', views.MyTargetsView.as_view(), name='target-my'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='target-leaderboard'),
    path('export/', views.TargetExportView.as_view(), name='target-export'),
    path('<int:pk>/', views.TargetDetailView.as_view(), name='target-detail'),
]

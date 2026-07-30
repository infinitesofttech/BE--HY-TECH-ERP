from django.urls import path
from . import views

urlpatterns = [
    path('backups/', views.BackupLogListCreateView.as_view()),
    path('backups/<int:pk>/', views.BackupLogDetailView.as_view()),
    path('backups/run/', views.BackupNowView.as_view()),
    path('cron-jobs/', views.CronJobListCreateView.as_view()),
    path('cron-jobs/<int:pk>/', views.CronJobDetailView.as_view()),
    path('cron-jobs/<int:pk>/toggle-active/', views.CronJobToggleActiveView.as_view()),
    path('banned-ips/', views.BannedIPListCreateView.as_view()),
    path('banned-ips/<int:pk>/', views.BannedIPDetailView.as_view()),
    path('connected-apps/', views.ConnectedAppListCreateView.as_view()),
    path('connected-apps/<int:pk>/', views.ConnectedAppDetailView.as_view()),
    path('info/', views.SystemInfoView.as_view()),
    path('clear-cache/', views.ClearCacheView.as_view()),
]

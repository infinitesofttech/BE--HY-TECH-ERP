from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.SendNotificationView.as_view(), name='notification-send'),
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('all/', views.AllSentNotificationsView.as_view(), name='notification-all-sent'),
    path('unread-count/', views.UnreadCountView.as_view(), name='notification-unread-count'),
    path('read-all/', views.MarkAllAsReadView.as_view(), name='notification-read-all'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/read/', views.MarkAsReadView.as_view(), name='notification-mark-read'),
]

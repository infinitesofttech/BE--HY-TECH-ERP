from django.urls import path
from .views import NotificationViewSet

urlpatterns = [
    path('', NotificationViewSet.as_view({
        'get': 'list',
    }), name='notification-list'),
    path('send/', NotificationViewSet.as_view({
        'post': 'create',
    }), name='notification-send'),
    path('<int:pk>/read/', NotificationViewSet.as_view({
        'patch': 'mark_read',
        'put': 'mark_read',
    }), name='notification-mark-read'),
]

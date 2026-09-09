from django.urls import path
from .views import ReminderViewSet

urlpatterns = [
    path('', ReminderViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='reminder-list'),
    path('<str:reminder_no>/', ReminderViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='reminder-detail'),
    path('<str:reminder_no>/follow-ups/', ReminderViewSet.as_view({
        'get': 'follow_ups',
        'post': 'follow_ups',
    }), name='reminder-follow-ups'),
    path('<str:reminder_no>/follow-ups/<int:follow_up_id>/', ReminderViewSet.as_view({
        'put': 'follow_up_detail',
        'patch': 'follow_up_detail',
        'delete': 'follow_up_detail',
    }), name='reminder-follow-up-detail'),
]

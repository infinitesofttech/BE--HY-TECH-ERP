from django.urls import path
from .views import PendingWorkViewSet

urlpatterns = [
    path('summary/', PendingWorkViewSet.as_view({
        'get': 'summary',
    }), name='pending-work-summary'),
    path('', PendingWorkViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='pending-work-list'),
    path('<str:pending_no>/', PendingWorkViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='pending-work-detail'),
]

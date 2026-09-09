from django.urls import path
from .views import ApplicationViewSet

urlpatterns = [
    path('', ApplicationViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='application-list'),
    path('<str:application_no>/', ApplicationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='application-detail'),
    path('<str:application_no>/status/', ApplicationViewSet.as_view({
        'patch': 'update_status',
        'put': 'update_status',
    }), name='application-status'),
    path('<str:application_no>/timeline/', ApplicationViewSet.as_view({
        'get': 'timeline',
    }), name='application-timeline'),
]

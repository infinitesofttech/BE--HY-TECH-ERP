from django.urls import path
from .views import AuditLogViewSet

urlpatterns = [
    path('', AuditLogViewSet.as_view({
        'get': 'list',
    }), name='audit-log-list'),
    path('<int:pk>/', AuditLogViewSet.as_view({
        'get': 'retrieve',
    }), name='audit-log-detail'),
]

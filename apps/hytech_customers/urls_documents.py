from django.urls import path
from .views import CustomerDocumentViewSet

urlpatterns = [
    path('<str:family_id>/<str:member_id>/', CustomerDocumentViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='customer-document-list'),
    path('<str:family_id>/<str:member_id>/<int:pk>/', CustomerDocumentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='customer-document-detail'),
]

from django.urls import path
from .views import (
    BaseServiceViewSet, SubServiceViewSet,
    RequiredDocumentViewSet, TransactionViewSet
)

urlpatterns = [
    # Sub Services (must be before <int:pk> of base services)
    path('sub-services/', SubServiceViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='sub-service-list'),
    path('sub-services/<int:pk>/', SubServiceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='sub-service-detail'),

    # Required Documents
    path('required-documents/', RequiredDocumentViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='required-document-list'),
    path('required-documents/<int:pk>/', RequiredDocumentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='required-document-detail'),

    # Transactions
    path('transactions/', TransactionViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='transaction-detail'),

    # Base Services
    path('', BaseServiceViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='service-list'),
    path('<int:pk>/', BaseServiceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='service-detail'),
]

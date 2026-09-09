from django.urls import path
from .views import (
    CustomerViewSet, FamilyMemberViewSet,
    CustomerDocumentViewSet, ServiceVisitViewSet
)

urlpatterns = [
    # Customers
    path('', CustomerViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='customer-list'),
    
    # Service Visits (must be above <family_id> to avoid capturing 'service-visits' as family_id!)
    path('service-visits/', ServiceVisitViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='service-visit-list'),
    path('service-visits/<str:visit_no>/', ServiceVisitViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='service-visit-detail'),
    path('service-visits/<str:visit_no>/documents/<int:doc_id>/', ServiceVisitViewSet.as_view({
        'patch': 'update_document',
        'put': 'update_document',
    }), name='service-visit-update-document'),

    # Customer Detail
    path('<str:family_id>/', CustomerViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='customer-detail'),

    # Family Members
    path('<str:family_id>/family-members/', FamilyMemberViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='family-member-list'),
    path('<str:family_id>/family-members/<int:pk>/', FamilyMemberViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='family-member-detail'),
]

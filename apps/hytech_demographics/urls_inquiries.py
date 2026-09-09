from django.urls import path
from .views import ContactInquiryViewSet

urlpatterns = [
    path('', ContactInquiryViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='inquiry-list'),
    path('<int:pk>/', ContactInquiryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='inquiry-detail'),
]

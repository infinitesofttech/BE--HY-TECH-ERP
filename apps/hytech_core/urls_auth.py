from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    StaffLoginView, CustomerLoginView,
    LogoutView, EmployeeViewSet
)

urlpatterns = [
    path('staff/login/', StaffLoginView.as_view(), name='staff-login'),
    path('customer/login/', CustomerLoginView.as_view(), name='customer-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Employees
    path('employees/', EmployeeViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='employee-list'),
    path('employees/<int:pk>/', EmployeeViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='employee-detail'),
]

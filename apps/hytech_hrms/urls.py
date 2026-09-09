from django.urls import path
from .views import (
    AttendanceViewSet, LeaveViewSet,
    LeaveBalanceView, HolidayViewSet
)

urlpatterns = [
    path('attendance/', AttendanceViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='hrms-attendance'),

    path('leaves/', LeaveViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='hrms-leaves'),
    path('leaves/<int:pk>/', LeaveViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='hrms-leave-detail'),

    path('leave-balance/<int:employee_id>/', LeaveBalanceView.as_view(), name='hrms-leave-balance'),

    path('holidays/', HolidayViewSet.as_view({
        'get': 'list',
    }), name='hrms-holidays'),
]

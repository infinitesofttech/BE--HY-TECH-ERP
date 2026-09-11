from django.urls import path
from .views import (
    AttendanceViewSet, LeaveViewSet,
    LeaveBalanceView, HolidayViewSet,
    AttendanceSummaryView, AttendanceReportView,
    LeaveSummaryView, LeaveReportView,
    EmployeeSummaryView, EmployeeDirectoryView,
    LateComingSummaryView, LateComingReportView,
    HRSettingsView, HRCompanySettingView,
    HRAttendanceSettingView, HRLeaveSettingView,
    HRNotificationSettingView, HRRolePermissionView,
    HRRolePermissionDetailView
)

urlpatterns = [
    # HR Settings (Company, Attendance, Leave, Notifications, Roles & Permissions)
    path('settings/', HRSettingsView.as_view(), name='hrms-settings'),
    path('settings/company/', HRCompanySettingView.as_view(), name='hrms-settings-company'),
    path('settings/attendance/', HRAttendanceSettingView.as_view(), name='hrms-settings-attendance'),
    path('settings/leave/', HRLeaveSettingView.as_view(), name='hrms-settings-leave'),
    path('settings/notifications/', HRNotificationSettingView.as_view(), name='hrms-settings-notifications'),
    path('settings/roles-permissions/', HRRolePermissionView.as_view(), name='hrms-settings-roles-permissions'),
    path('settings/roles-permissions/<int:pk>/', HRRolePermissionDetailView.as_view(), name='hrms-settings-role-permission-detail'),

    path('late-coming/summary/', LateComingSummaryView.as_view(), name='hrms-late-coming-summary'),
    path('late-coming/report/', LateComingReportView.as_view(), name='hrms-late-coming-report'),

    path('employees/summary/', EmployeeSummaryView.as_view(), name='hrms-employees-summary'),
    path('employees/report/', EmployeeDirectoryView.as_view(), name='hrms-employees-report'),

    path('attendance/summary/', AttendanceSummaryView.as_view(), name='hrms-attendance-summary'),
    path('attendance/report/', AttendanceReportView.as_view(), name='hrms-attendance-report'),

    path('leaves/summary/', LeaveSummaryView.as_view(), name='hrms-leaves-summary'),
    path('leaves/report/', LeaveReportView.as_view(), name='hrms-leaves-report'),

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

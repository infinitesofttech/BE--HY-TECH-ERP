from django.urls import path
from . import views

urlpatterns = [
    path('types/', views.AttendanceTypeListCreateView.as_view(), name='attendance-types'),
    path('types/<int:pk>/', views.AttendanceTypeDetailView.as_view(), name='attendance-type-detail'),
    path('punch-in/', views.AttendancePunchInView.as_view(), name='attendance-punch-in'),
    path('punch-out/', views.AttendancePunchOutView.as_view(), name='attendance-punch-out'),
    path('today/', views.TodayAttendanceView.as_view(), name='attendance-today'),
    path('history/', views.AttendanceHistoryView.as_view(), name='attendance-history'),
    path('report/daily/', views.AttendanceDailyReportView.as_view(), name='attendance-report-daily'),
    path('report/monthly/', views.AttendanceMonthlyReportView.as_view(), name='attendance-report-monthly'),
    path('report/export/', views.AttendanceExportView.as_view(), name='attendance-report-export'),
]

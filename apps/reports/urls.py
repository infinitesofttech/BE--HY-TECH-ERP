from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='report-dashboard'),
    path('performance/', views.PerformanceOverviewView.as_view(), name='report-performance'),
    path('compare/', views.CompareEmployeesView.as_view(), name='report-compare'),
    path('weak-areas/', views.WeakAreaAnalysisView.as_view(), name='report-weak-areas'),
    path('leads/', views.LeadReportView.as_view(), name='report-leads'),
    path('deals/', views.DealReportView.as_view(), name='report-deals'),
    path('contacts/', views.ContactReportView.as_view(), name='report-contacts'),
    path('companies/', views.CompanyReportView.as_view(), name='report-companies'),
    path('revenue/', views.RevenueReportView.as_view(), name='report-revenue'),
    path('projects/', views.ProjectReportView.as_view(), name='report-projects'),
    path('tasks/', views.TaskReportView.as_view(), name='report-tasks'),
    path('attendance/', views.AttendanceReportView.as_view(), name='report-attendance'),
    path('leaves/', views.LeaveReportView.as_view(), name='report-leaves'),
    path('customer-analytics/', views.CustomerAnalyticsView.as_view(), name='report-customer-analytics'),
]

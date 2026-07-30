from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='report-dashboard'),
    path('performance/', views.PerformanceOverviewView.as_view(), name='report-performance'),
    path('compare/', views.CompareEmployeesView.as_view(), name='report-compare'),
    path('weak-areas/', views.WeakAreaAnalysisView.as_view(), name='report-weak-areas'),
]

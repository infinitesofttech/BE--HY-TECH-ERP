from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.SalesReportCreateView.as_view(), name='sales-report-create'),
    path('reports/', views.SalesReportListView.as_view(), name='sales-report-list'),
    path('reports/<int:pk>/', views.SalesReportDetailView.as_view(), name='sales-report-detail'),
    path('daily/', views.DailySalesReportView.as_view(), name='sales-daily'),
    path('monthly/', views.MonthlySalesReportView.as_view(), name='sales-monthly'),
    path('employee/<int:employee_id>/', views.EmployeeSalesView.as_view(), name='sales-employee'),
    path('export/', views.SalesExportView.as_view(), name='sales-export'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.SalesReportListView.as_view(), name='sales-report-list'),
    path('reports/<int:pk>/', views.SalesReportDetailView.as_view(), name='sales-report-detail'),
    path('daily/', views.DailySalesReportView.as_view(), name='sales-daily'),
    path('monthly/', views.MonthlySalesReportView.as_view(), name='sales-monthly'),
    path('employee/<int:employee_id>/', views.EmployeeSalesView.as_view(), name='sales-employee'),
    path('export/', views.SalesExportView.as_view(), name='sales-export'),
    path('customers/', views.CustomerListCreateView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('feedback/', views.CustomerFeedbackListCreateView.as_view(), name='customer-feedback-list'),
    path('feedback/<int:pk>/', views.CustomerFeedbackDetailView.as_view(), name='customer-feedback-detail'),
    path('orders/', views.SalesOrderListCreateView.as_view(), name='sales-order-list'),
    path('orders/<int:pk>/', views.SalesOrderDetailView.as_view(), name='sales-order-detail'),
    path('orders/<int:pk>/start-production/', views.SalesOrderStartProductionView.as_view(), name='sales-order-start-production'),
    path('refunds/', views.RefundListCreateView.as_view(), name='refund-list'),
    path('refunds/<int:pk>/', views.RefundDetailView.as_view(), name='refund-detail'),
    path('delivery-notes/', views.DeliveryNoteListCreateView.as_view(), name='delivery-note-list'),
    path('delivery-notes/<int:pk>/', views.DeliveryNoteDetailView.as_view(), name='delivery-note-detail'),
    path('delivery-notes/<int:pk>/toggle-active/', views.DeliveryNoteToggleActiveView.as_view(), name='delivery-note-toggle'),
    path('delivery-notes/<int:pk>/create-invoice/', views.DeliveryNoteCreateInvoiceView.as_view(), name='delivery-note-create-invoice'),
    path('analysis/', views.SalesAnalysisView.as_view(), name='sales-analysis'),
]

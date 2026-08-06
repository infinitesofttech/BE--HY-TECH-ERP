from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderCreateView.as_view(), name='order-create'),
    path('list/', views.OrderListView.as_view(), name='order-list'),
    path('my/', views.MyOrdersView.as_view(), name='order-my'),
    path('export/', views.OrderExportView.as_view(), name='order-export'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status'),
    path('quotations/', views.QuotationListCreateView.as_view(), name='quotation-list'),
    path('quotations/<int:pk>/', views.QuotationDetailView.as_view(), name='quotation-detail'),
    path('quotations/<int:pk>/send/', views.QuotationSendView.as_view(), name='quotation-send'),
    path('quotations/<int:pk>/approve/', views.QuotationApproveView.as_view(), name='quotation-approve'),
    path('quotations/<int:pk>/reject/', views.QuotationRejectView.as_view(), name='quotation-reject'),
]

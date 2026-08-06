from django.urls import path
from . import views

urlpatterns = [
    path('vendors/', views.VendorListCreateView.as_view(), name='vendor-list-create'),
    path('vendors/<int:pk>/', views.VendorDetailView.as_view(), name='vendor-detail'),
    path('', views.PurchaseListCreateView.as_view(), name='purchase-list-create'),
    path('<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase-detail'),
    path('purchase-orders/', views.PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),
    path('purchase-orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
    path('purchase-returns/', views.PurchaseReturnListCreateView.as_view(), name='purchase-return-list-create'),
    path('purchase-returns/<int:pk>/', views.PurchaseReturnDetailView.as_view(), name='purchase-return-detail'),
    path('analytics/', views.PurchaseAnalyticsView.as_view(), name='purchase-analytics'),
]

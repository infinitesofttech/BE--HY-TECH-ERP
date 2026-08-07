from django.urls import path
from . import views

urlpatterns = [
    path('analytics/', views.AssetAnalyticsView.as_view(), name='asset-analytics'),
    path('registrations/', views.AssetRegistrationListCreateView.as_view(), name='asset-registration-list'),
    path('registrations/<int:pk>/', views.AssetRegistrationDetailView.as_view(), name='asset-registration-detail'),
    path('assignments/', views.AssetAssignmentListCreateView.as_view(), name='asset-assignment-list'),
    path('assignments/<int:pk>/', views.AssetAssignmentDetailView.as_view(), name='asset-assignment-detail'),
    path('depreciations/', views.AssetDepreciationListCreateView.as_view(), name='asset-depreciation-list'),
    path('depreciations/<int:pk>/', views.AssetDepreciationDetailView.as_view(), name='asset-depreciation-detail'),
    path('maintenances/', views.AssetMaintenanceListCreateView.as_view(), name='asset-maintenance-list'),
    path('maintenances/<int:pk>/', views.AssetMaintenanceDetailView.as_view(), name='asset-maintenance-detail'),
    path('disposals/', views.AssetDisposalListCreateView.as_view(), name='asset-disposal-list'),
    path('disposals/<int:pk>/', views.AssetDisposalDetailView.as_view(), name='asset-disposal-detail'),
]

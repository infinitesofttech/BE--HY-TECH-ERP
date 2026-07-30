from django.urls import path
from . import views

urlpatterns = [
    path('stages/', views.PipelineStageListCreateView.as_view(), name='pipeline-stage-list'),
    path('stages/<int:pk>/', views.PipelineStageDetailView.as_view(), name='pipeline-stage-detail'),
    path('leads/', views.LeadListCreateView.as_view(), name='lead-list'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead-detail'),
    path('deals/', views.DealListCreateView.as_view(), name='deal-list'),
    path('deals/<int:pk>/', views.DealDetailView.as_view(), name='deal-detail'),
    path('deals/pipeline/', views.DealPipelineView.as_view(), name='deal-pipeline'),
    path('deals/<int:deal_pk>/activities/', views.DealActivityListCreateView.as_view(), name='deal-activity-list'),
    path('deals/<int:deal_pk>/activities/<int:pk>/', views.DealActivityDetailView.as_view(), name='deal-activity-detail'),
]

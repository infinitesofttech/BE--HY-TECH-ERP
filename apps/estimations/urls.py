from django.urls import path
from . import views

urlpatterns = [
    path('estimations/', views.EstimationListCreateView.as_view(), name='estimation-list'),
    path('estimations/<int:pk>/', views.EstimationDetailView.as_view(), name='estimation-detail'),
    path('proposals/', views.ProposalListCreateView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', views.ProposalDetailView.as_view(), name='proposal-detail'),
]

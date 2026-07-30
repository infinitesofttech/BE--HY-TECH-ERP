from django.urls import path
from . import views

urlpatterns = [
    path('contracts/', views.ContractListCreateView.as_view(), name='contract-list'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
]

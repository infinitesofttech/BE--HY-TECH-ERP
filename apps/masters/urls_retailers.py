from django.urls import path
from . import views

urlpatterns = [
    path('', views.RetailerListCreateView.as_view(), name='retailer-list'),
    path('<int:pk>/', views.RetailerDetailView.as_view(), name='retailer-detail'),
    path('<int:pk>/toggle-status/', views.RetailerToggleStatusView.as_view(), name='retailer-toggle-status'),
]

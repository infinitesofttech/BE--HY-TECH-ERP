from django.urls import path
from . import views

urlpatterns = [
    path('', views.DealerListCreateView.as_view(), name='dealer-list'),
    path('<int:pk>/', views.DealerDetailView.as_view(), name='dealer-detail'),
    path('<int:pk>/toggle-status/', views.DealerToggleStatusView.as_view(), name='dealer-toggle-status'),
]

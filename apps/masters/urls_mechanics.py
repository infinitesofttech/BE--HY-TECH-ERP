from django.urls import path
from . import views

urlpatterns = [
    path('', views.MechanicListCreateView.as_view(), name='mechanic-list'),
    path('<int:pk>/', views.MechanicDetailView.as_view(), name='mechanic-detail'),
    path('<int:pk>/toggle-status/', views.MechanicToggleStatusView.as_view(), name='mechanic-toggle-status'),
]

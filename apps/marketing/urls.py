from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.CampaignListCreateView.as_view(), name='campaign-list'),
    path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<int:pk>/archive/', views.CampaignArchiveView.as_view(), name='campaign-archive'),
    path('campaigns/<int:pk>/send/', views.CampaignSendView.as_view(), name='campaign-send'),
]

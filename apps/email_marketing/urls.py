from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.EmailTemplateListCreateView.as_view(), name='email-template-list'),
    path('templates/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='email-template-detail'),
    path('campaigns/', views.EmailCampaignListCreateView.as_view(), name='email-campaign-list'),
    path('campaigns/<int:pk>/', views.EmailCampaignDetailView.as_view(), name='email-campaign-detail'),
    path('subscriber-lists/', views.SubscriberListListCreateView.as_view(), name='subscriber-list'),
    path('subscriber-lists/<int:pk>/', views.SubscriberListDetailView.as_view(), name='subscriber-list-detail'),
    path('engagement/', views.EmailEngagementReportView.as_view(), name='email-engagement'),
]

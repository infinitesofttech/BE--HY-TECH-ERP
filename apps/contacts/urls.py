from django.urls import path
from . import views

urlpatterns = [
    path('companies/', views.CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company-detail'),
    path('companies/<int:pk>/toggle-status/', views.CompanyToggleStatusView.as_view(), name='company-toggle-status'),
    path('contacts/', views.ContactListCreateView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('messages/', views.ContactMessageListCreateView.as_view(), name='contact-message-list'),
    path('messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='contact-message-detail'),
]

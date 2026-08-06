from django.urls import path
from . import views

urlpatterns = [
    path('currencies/', views.CurrencyListCreateView.as_view(), name='currency-list'),
    path('currencies/<int:pk>/', views.CurrencyDetailView.as_view(), name='currency-detail'),
    path('sources/', views.SourceListCreateView.as_view(), name='source-list'),
    path('sources/<int:pk>/', views.SourceDetailView.as_view(), name='source-detail'),
    path('industries/', views.IndustryListCreateView.as_view(), name='industry-list'),
    path('industries/<int:pk>/', views.IndustryDetailView.as_view(), name='industry-detail'),
    path('contact-stages/', views.ContactStageListCreateView.as_view(), name='contact-stage-list'),
    path('contact-stages/<int:pk>/', views.ContactStageDetailView.as_view(), name='contact-stage-detail'),
    path('lost-reasons/', views.LostReasonListCreateView.as_view(), name='lost-reason-list'),
    path('lost-reasons/<int:pk>/', views.LostReasonDetailView.as_view(), name='lost-reason-detail'),
    path('call-reasons/', views.CallReasonListCreateView.as_view(), name='call-reason-list'),
    path('call-reasons/<int:pk>/', views.CallReasonDetailView.as_view(), name='call-reason-detail'),
    path('call-logs/', views.CallLogListCreateView.as_view(), name='call-log-list'),
    path('call-logs/<int:pk>/', views.CallLogDetailView.as_view(), name='call-log-detail'),
]

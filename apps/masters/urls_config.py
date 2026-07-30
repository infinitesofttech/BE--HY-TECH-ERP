from django.urls import path
from . import views

urlpatterns = [
    path('tax-rates/', views.TaxRateListCreateView.as_view(), name='tax-rate-list'),
    path('tax-rates/<int:pk>/', views.TaxRateDetailView.as_view(), name='tax-rate-detail'),
    path('currencies/', views.CurrencyListCreateView.as_view(), name='currency-list'),
    path('currencies/<int:pk>/', views.CurrencyDetailView.as_view(), name='currency-detail'),
    path('sources/', views.SourceListCreateView.as_view(), name='source-list'),
    path('sources/<int:pk>/', views.SourceDetailView.as_view(), name='source-detail'),
    path('industries/', views.IndustryListCreateView.as_view(), name='industry-list'),
    path('industries/<int:pk>/', views.IndustryDetailView.as_view(), name='industry-detail'),
]

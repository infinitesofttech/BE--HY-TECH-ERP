from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.DepartmentListCreateView.as_view()),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view()),
    path('states/', views.StateListCreateView.as_view()),
    path('states/<int:pk>/', views.StateDetailView.as_view()),
    path('cities/', views.CityListCreateView.as_view()),
    path('cities/<int:pk>/', views.CityDetailView.as_view()),
    path('custom-fields/', views.CustomFieldListCreateView.as_view()),
    path('custom-fields/<int:pk>/', views.CustomFieldDetailView.as_view()),
    path('prefixes/', views.PrefixSettingListCreateView.as_view()),
    path('prefixes/<int:pk>/', views.PrefixSettingDetailView.as_view()),
    path('prefixes/<int:pk>/next/', views.PrefixSettingNextNumberView.as_view()),
    path('printers/', views.PrinterSettingListCreateView.as_view()),
    path('printers/<int:pk>/', views.PrinterSettingDetailView.as_view()),
    path('gdpr/', views.GDPRConsentListCreateView.as_view()),
    path('localization/', views.LocalizationSettingView.as_view()),
    path('languages/', views.LanguageSettingListCreateView.as_view()),
    path('languages/<int:pk>/', views.LanguageSettingDetailView.as_view()),
    path('appearance/', views.AppearanceSettingView.as_view()),
    path('invoice-settings/', views.InvoiceSettingView.as_view()),
    path('security-settings/', views.SecuritySettingView.as_view()),
]

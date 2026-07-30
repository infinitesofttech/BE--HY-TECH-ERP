from django.urls import path

from . import views

urlpatterns = [
    path('bank-accounts/', views.BankAccountListCreateView.as_view()),
    path('bank-accounts/<int:pk>/', views.BankAccountDetailView.as_view()),
    path('purchases/', views.PurchaseTransactionListCreateView.as_view()),
    path('purchases/<int:pk>/', views.PurchaseTransactionDetailView.as_view()),
    path('payment-gateways/', views.PaymentGatewayListCreateView.as_view()),
    path('payment-gateways/<int:pk>/', views.PaymentGatewayDetailView.as_view()),
    path('discount-rules/', views.DiscountRuleListCreateView.as_view()),
    path('discount-rules/<int:pk>/', views.DiscountRuleDetailView.as_view()),
    path('discount-rules/<int:pk>/toggle-active/', views.DiscountRuleToggleActiveView.as_view()),
]

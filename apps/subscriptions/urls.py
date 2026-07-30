from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.MembershipPlanListCreateView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', views.MembershipPlanDetailView.as_view(), name='plan-detail'),
    path('addons/', views.MembershipAddonListCreateView.as_view(), name='addon-list'),
    path('addons/<int:pk>/', views.MembershipAddonDetailView.as_view(), name='addon-detail'),
    path('subscriptions/', views.SubscriptionListCreateView.as_view(), name='subscription-list'),
    path('subscriptions/my/', views.MySubscriptionView.as_view(), name='subscription-my'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('transactions/', views.SubscriptionTransactionListCreateView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.SubscriptionTransactionDetailView.as_view(), name='transaction-detail'),
]

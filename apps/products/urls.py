from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.ProductCategoryListCreateView.as_view(), name='product-category-list'),
    path('categories/<int:pk>/', views.ProductCategoryDetailView.as_view(), name='product-category-detail'),
    path('', views.ProductListCreateView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/toggle-active/', views.ProductToggleActiveView.as_view(), name='product-toggle-active'),
    path('catalogue/', views.ProductCatalogueView.as_view(), name='product-catalogue'),
    path('tour-plans/', views.TourPlanListCreateView.as_view(), name='tour-plan-list'),
    path('tour-plans/<int:pk>/', views.TourPlanDetailView.as_view(), name='tour-plan-detail'),
    path('tour-plans/<int:pk>/toggle-active/', views.TourPlanToggleActiveView.as_view(), name='tour-plan-toggle'),
    path('policies/', views.PolicyListCreateView.as_view(), name='policy-list'),
    path('policies/<int:pk>/', views.PolicyDetailView.as_view(), name='policy-detail'),
    path('policies/<int:pk>/toggle-active/', views.PolicyToggleActiveView.as_view(), name='policy-toggle'),
]

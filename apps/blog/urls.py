from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.BlogCategoryListCreateView.as_view(), name='blog-category-list'),
    path('categories/<int:pk>/', views.BlogCategoryDetailView.as_view(), name='blog-category-detail'),
    path('posts/', views.BlogPostListCreateView.as_view(), name='blog-post-list'),
    path('posts/<int:pk>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
    path('comments/', views.BlogCommentListCreateView.as_view(), name='blog-comment-list'),
    path('comments/<int:pk>/', views.BlogCommentDetailView.as_view(), name='blog-comment-detail'),
    path('tags/', views.BlogTagListCreateView.as_view(), name='blog-tag-list'),
    path('tags/<int:pk>/', views.BlogTagDetailView.as_view(), name='blog-tag-detail'),
]

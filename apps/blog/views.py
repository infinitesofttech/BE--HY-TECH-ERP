from drf_spectacular.utils import extend_schema
from rest_framework import generics, filters
from .models import BlogCategory, BlogPost, BlogComment, BlogTag
from .serializers import (
    BlogCategorySerializer,
    BlogPostSerializer,
    BlogCommentSerializer,
    BlogTagSerializer,
)
from apps.accounts.permissions import IsSuperAdmin


@extend_schema(tags=['Blog Categories'])
class BlogCategoryListCreateView(generics.ListCreateAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


@extend_schema(tags=['Blog Categories'])
class BlogCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


@extend_schema(tags=['Blog Posts'])
class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.select_related('author', 'category').all()
    serializer_class = BlogPostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt', 'tags']
    ordering_fields = ['created_at', 'published_at', 'title']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == 'GET':
            return queryset.filter(status='published')
        return queryset

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


@extend_schema(tags=['Blog Posts'])
class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.select_related('author', 'category').all()
    serializer_class = BlogPostSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == 'GET':
            return queryset.filter(status='published')
        return queryset


@extend_schema(tags=['Blog Comments'])
class BlogCommentListCreateView(generics.ListCreateAPIView):
    queryset = BlogComment.objects.select_related('post').all()
    serializer_class = BlogCommentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'content']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsSuperAdmin()]
        return []


@extend_schema(tags=['Blog Comments'])
class BlogCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogComment.objects.select_related('post').all()
    serializer_class = BlogCommentSerializer

    def get_permissions(self):
        return [IsSuperAdmin()]


@extend_schema(tags=['Blog Tags'])
class BlogTagListCreateView(generics.ListCreateAPIView):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


@extend_schema(tags=['Blog Tags'])
class BlogTagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []

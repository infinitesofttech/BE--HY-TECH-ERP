from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogComment, BlogTag


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'author', 'category', 'published_at', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'content', 'excerpt', 'tags']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'email', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    search_fields = ['name', 'email', 'content']
    readonly_fields = ['created_at']


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['created_at']

from django.contrib import admin
from .models import (
    FAQ, Testimonial, SocialFeedPost, StaticPage,
    FileManagerFile, Note,
)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'company', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'rating']
    search_fields = ['customer_name', 'company', 'content']


@admin.register(SocialFeedPost)
class SocialFeedPostAdmin(admin.ModelAdmin):
    list_display = ['platform', 'posted_at', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['content']


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'published_at', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title', 'content', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(FileManagerFile)
class FileManagerFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_type', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type']
    search_fields = ['name', 'folder']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_pinned', 'color', 'updated_at']
    list_filter = ['is_pinned']
    search_fields = ['title', 'content']

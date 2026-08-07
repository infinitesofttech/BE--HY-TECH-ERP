from rest_framework import serializers
from .models import BlogCategory, BlogPost, BlogComment, BlogTag


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'author', 'author_name', 'category', 'category_name', 'tags',
            'status', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        if obj.author is None:
            return ''
        return obj.author.get_full_name() or obj.author.email

    def get_category_name(self, obj):
        if obj.category is None:
            return ''
        return obj.category.name


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'name', 'email', 'content', 'is_approved', 'created_at']
        read_only_fields = ['id', 'is_approved', 'created_at']


class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'name', 'slug', 'status', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

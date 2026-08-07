from rest_framework import serializers
from .models import (
    FAQ, Testimonial, SocialFeedPost, StaticPage,
    FileManagerFile, Note,
)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class FAQCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'order', 'is_active']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'customer_name', 'company', 'content', 'rating', 'image', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TestimonialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['customer_name', 'company', 'content', 'rating', 'image', 'is_active']


class SocialFeedPostSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = SocialFeedPost
        fields = ['id', 'platform', 'platform_display', 'post_url', 'content', 'posted_at', 'is_active', 'created_at']
        read_only_fields = ['id', 'platform_display', 'created_at']


class SocialFeedPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialFeedPost
        fields = ['platform', 'post_url', 'content', 'posted_at', 'is_active']


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = [
            'id', 'title', 'slug', 'content', 'meta_title', 'meta_description',
            'is_published', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaticPageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = [
            'title', 'slug', 'content', 'meta_title', 'meta_description',
            'is_published', 'published_at',
        ]


class FileManagerFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FileManagerFile
        fields = [
            'id', 'name', 'file', 'file_url', 'folder', 'file_type',
            'file_size', 'uploaded_by', 'uploaded_by_name', 'uploaded_at',
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_by', 'uploaded_at']

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by is None:
            return ''
        return obj.uploaded_by.get_full_name() or obj.uploaded_by.email

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file is None or not request:
            return ''
        return request.build_absolute_uri(obj.file.url)

    def create(self, validated_data):
        uploaded_file = validated_data.get('file')
        if uploaded_file:
            validated_data['file_size'] = uploaded_file.size
            import os
            name = validated_data.get('name', '')
            if not name:
                validated_data['name'] = os.path.basename(uploaded_file.name)
            ext = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
            if ext:
                validated_data['file_type'] = ext
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'user', 'is_pinned', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'content', 'is_pinned', 'color']

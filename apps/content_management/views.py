from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from drf_spectacular.utils import extend_schema
from apps.accounts.permissions import IsManagerOrAbove
from .models import (
    FAQ, Testimonial, SocialFeedPost, StaticPage,
    FileManagerFile, Note,
)
from .serializers import (
    FAQSerializer, FAQCreateSerializer,
    TestimonialSerializer, TestimonialCreateSerializer,
    SocialFeedPostSerializer, SocialFeedPostCreateSerializer,
    StaticPageSerializer, StaticPageCreateSerializer,
    FileManagerFileSerializer,
    NoteSerializer, NoteCreateSerializer,
)


@extend_schema(tags=['FAQ'])
class FAQListCreateView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['question', 'answer', 'category']
    ordering_fields = ['order', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FAQCreateSerializer
        return FAQSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return FAQ.objects.filter(is_active=True)
        return FAQ.objects.all()


@extend_schema(tags=['FAQ'])
class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return FAQCreateSerializer
        return FAQSerializer


@extend_schema(tags=['Testimonials'])
class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_name', 'company', 'content']
    ordering_fields = ['rating', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TestimonialCreateSerializer
        return TestimonialSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Testimonial.objects.filter(is_active=True)
        return Testimonial.objects.all()


@extend_schema(tags=['Testimonials'])
class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TestimonialCreateSerializer
        return TestimonialSerializer


@extend_schema(tags=['Social Feed'])
class SocialFeedPostListCreateView(generics.ListCreateAPIView):
    queryset = SocialFeedPost.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content', 'platform']
    ordering_fields = ['posted_at', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SocialFeedPostCreateSerializer
        return SocialFeedPostSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return SocialFeedPost.objects.filter(is_active=True)
        return SocialFeedPost.objects.all()


@extend_schema(tags=['Social Feed'])
class SocialFeedPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SocialFeedPost.objects.all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return SocialFeedPostCreateSerializer
        return SocialFeedPostSerializer


@extend_schema(tags=['Static Pages'])
class StaticPageListCreateView(generics.ListCreateAPIView):
    queryset = StaticPage.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'meta_title', 'meta_description']
    ordering_fields = ['title', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StaticPageCreateSerializer
        return StaticPageSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return StaticPage.objects.filter(is_published=True)
        return StaticPage.objects.all()


@extend_schema(tags=['Static Pages'])
class StaticPageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StaticPage.objects.all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return StaticPageCreateSerializer
        return StaticPageSerializer

    def get_object(self):
        lookup = self.kwargs.get('slug')
        if lookup and self.kwargs.get('pk') is None:
            self.lookup_field = 'slug'
            self.lookup_url_kwarg = 'slug'
        return super().get_object()


@extend_schema(tags=['File Manager'])
class FileManagerFileListCreateView(generics.ListCreateAPIView):
    queryset = FileManagerFile.objects.select_related('uploaded_by').all()
    serializer_class = FileManagerFileSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'folder', 'file_type']
    ordering_fields = ['file_size', 'uploaded_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['File Manager'])
class FileManagerFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileManagerFile.objects.select_related('uploaded_by').all()
    serializer_class = FileManagerFileSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Notes'])
class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['is_pinned', 'updated_at', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NoteCreateSerializer
        return NoteSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Notes'])
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return NoteCreateSerializer
        return NoteSerializer

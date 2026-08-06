from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Company, Contact, ContactMessage
from .serializers import CompanySerializer, ContactSerializer, ContactMessageSerializer
from apps.accounts.permissions import IsManagerOrAbove


class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'industry', 'owner']
    search_fields = ['name', 'email', 'city', 'industry__name']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    @extend_schema(request=CompanySerializer, responses={201: CompanySerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @extend_schema(request=CompanySerializer, responses={200: CompanySerializer})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(request=CompanySerializer, responses={200: CompanySerializer})
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CompanyToggleStatusView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    @extend_schema(
        request=None,
        responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}}}},
    )
    def patch(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)
        company.status = 'inactive' if company.status == 'active' else 'active'
        company.save()
        return Response({'status': company.status})


class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'owner', 'source', 'type', 'visibility', 'industry']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'job_title', 'company__name']
    ordering_fields = ['first_name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    @extend_schema(request=ContactSerializer, responses={201: ContactSerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @extend_schema(request=ContactSerializer, responses={200: ContactSerializer})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(request=ContactSerializer, responses={200: ContactSerializer})
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ContactMessageListCreateView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'email', 'phone', 'message']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            from rest_framework.permissions import AllowAny
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(request=ContactMessageSerializer, responses={201: ContactMessageSerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

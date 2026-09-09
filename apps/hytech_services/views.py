from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import BaseService, SubService, RequiredDocument, Transaction
from .serializers import (
    BaseServiceSerializer, SubServiceSerializer,
    RequiredDocumentSerializer, TransactionSerializer
)


class BaseServiceViewSet(viewsets.ModelViewSet):
    queryset = BaseService.objects.all().prefetch_related('sub_services__required_documents')
    serializer_class = BaseServiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['Category', 'ServiceType', 'IsActive', 'Priority']
    search_fields = ['ServiceName', 'ServiceNameGu', 'Description', 'Department', 'SubCategory']
    ordering_fields = ['id', 'ServiceName', 'TotalFee', 'SlaDays', 'CreatedAt']
    ordering = ['id']


class SubServiceViewSet(viewsets.ModelViewSet):
    queryset = SubService.objects.all().prefetch_related('required_documents')
    serializer_class = SubServiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['Service', 'IsActive']
    search_fields = ['SubServiceName', 'Description']
    ordering = ['id']


class RequiredDocumentViewSet(viewsets.ModelViewSet):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['SubService', 'document_type', 'IsRequired']
    search_fields = ['DocumentName']
    ordering = ['id']


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().select_related('customer', 'service', 'sub_service', 'staff')
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'service', 'payment_status', 'payment_mode']
    search_fields = ['transaction_no', 'customer__head_of_family', 'customer__mobile_number', 'customer__family_id', 'remarks']
    ordering_fields = ['transaction_date', 'bill_amount', 'created_at']
    ordering = ['-created_at']

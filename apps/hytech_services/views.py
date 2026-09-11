from django.db.models import Sum, Count
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal

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



class ServiceSummaryAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        total_base_services = BaseService.objects.count()
        total_sub_services = SubService.objects.count()
        total_required_documents = RequiredDocument.objects.count()

        return Response(
            {
                "total_base_services": total_base_services,
                "total_sub_services": total_sub_services,
                "total_required_documents": total_required_documents,
            },
            status=status.HTTP_200_OK
        )


class RevenueAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Transaction.objects.all()

        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')

        if from_date:
            queryset = queryset.filter(transaction_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(transaction_date__lte=to_date)

        by_mode = list(
            queryset.values('payment_mode')
            .annotate(
                count=Count('id'),
                total_billed=Sum('bill_amount'),
                total_collected=Sum('paid_amount'),
                total_due=Sum('due_amount'),
            )
            .order_by('-total_collected')
        )

        by_status = list(
            queryset.values('payment_status')
            .annotate(
                count=Count('id'),
                total_billed=Sum('bill_amount'),
                total_collected=Sum('paid_amount'),
                total_due=Sum('due_amount'),
            )
            .order_by('payment_status')
        )

        totals = queryset.aggregate(
            total_transactions=Count('id'),
            total_billing=Sum('bill_amount'),
            total_collected=Sum('paid_amount'),
            total_due=Sum('due_amount'),
            total_points_earned=Sum('points_earned'),
            total_wallet_credit=Sum('wallet_credit'),
            total_wallet_used=Sum('wallet_used'),
        )

        for key in ('total_billing', 'total_collected', 'total_due',
                    'total_wallet_credit', 'total_wallet_used'):
            if totals.get(key) is None:
                totals[key] = Decimal('0.00')

        return Response(
            {
                "date_range": {
                    "from": from_date,
                    "to": to_date,
                },
                "summary": totals,
                "by_payment_mode": by_mode,
                "by_payment_status": by_status,
            },
            status=status.HTTP_200_OK
        )
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.http import HttpResponse
from datetime import datetime
import openpyxl

from .models import Order, OrderItem, Quotation, QuotationItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
    QuotationSerializer,
    QuotationCreateSerializer,
)
from . import services
from apps.accounts.permissions import IsManagerOrAbove


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['employee', 'dealer', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'notes']
    ordering_fields = ['created_at', 'total_amount', 'status']

    def get_queryset(self):
        queryset = Order.objects.select_related(
            'employee', 'dealer',
        ).prefetch_related('items__product').all()

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.select_related(
        'employee', 'dealer',
    ).prefetch_related('items__product').all()
    serializer_class = OrderSerializer


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(
            employee=self.request.user,
        ).select_related(
            'employee', 'dealer',
        ).prefetch_related('items__product')


class OrderStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsManagerOrAbove]
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            OrderSerializer(instance).data,
            status=status.HTTP_200_OK,
        )


class OrderExportView(APIView):
    # permission_classes = [IsManagerOrAbove]

    def get(self, request):
        orders = Order.objects.select_related(
            'employee', 'dealer',
        ).prefetch_related('items__product').all()

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)
        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)
        if status_filter:
            orders = orders.filter(status=status_filter)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Orders'

        headers = [
            'Order ID', 'Employee', 'Dealer', 'Status',
            'Total Amount', 'Notes', 'Created At',
        ]
        ws.append(headers)

        for order in orders:
            ws.append([
                order.id,
                order.employee.get_full_name() or order.employee.email,
                order.dealer.name if order.dealer else 'N/A',
                order.get_status_display(),
                float(order.total_amount),
                order.notes,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        ws.append([])
        ws.append(['Items Detail'])
        ws.append([
            'Order ID', 'Product', 'Quantity', 'Unit Price', 'Total',
        ])
        for order in orders:
            for item in order.items.select_related('product').all():
                ws.append([
                    order.id,
                    item.product.name,
                    item.quantity,
                    float(item.unit_price),
                    float(item.total),
                ])

        for column in ws.columns:
            max_length = 0
            col_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_length + 2, 50)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f'orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response


class QuotationListCreateView(generics.ListCreateAPIView):
    queryset = Quotation.objects.prefetch_related('items__product').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'client']
    search_fields = ['quote_id', 'client', 'notes']
    ordering_fields = ['quote_date', 'valid_till', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuotationCreateSerializer
        return QuotationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quotation = serializer.save(created_by=request.user)
        return Response(
            QuotationSerializer(quotation).data,
            status=status.HTTP_201_CREATED,
        )


class QuotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quotation.objects.prefetch_related('items__product').all()
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class QuotationSendView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuotationSerializer

    @extend_schema(responses={200: QuotationSerializer})
    def post(self, request, pk):
        quotation = Quotation.objects.get(pk=pk)
        services.send_quotation(quotation)
        quotation.refresh_from_db()
        return Response(
            QuotationSerializer(quotation).data, status=status.HTTP_200_OK,
        )


class QuotationApproveView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    serializer_class = QuotationSerializer

    @extend_schema(responses={201: {
        'type': 'object',
        'properties': {
            'quotation': {'$ref': '#/components/schemas/Quotation'},
            'sales_order': {'$ref': '#/components/schemas/SalesOrder'},
        },
    }})
    def post(self, request, pk):
        quotation = Quotation.objects.get(pk=pk)
        if quotation.status != 'sent' and quotation.status != 'accepted':
            return Response(
                {'detail': 'Only sent quotations can be approved.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.sales.serializers import SalesOrderSerializer
        sales_order = services.approve_quotation(
            quotation, employee=request.user,
        )
        quotation.refresh_from_db()
        return Response({
            'quotation': QuotationSerializer(quotation).data,
            'sales_order': SalesOrderSerializer(sales_order).data,
        }, status=status.HTTP_201_CREATED)


class QuotationRejectView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    serializer_class = QuotationSerializer

    @extend_schema(responses={200: QuotationSerializer})
    def post(self, request, pk):
        quotation = Quotation.objects.get(pk=pk)
        services.reject_quotation(
            quotation, lost_reason=request.data.get('lost_reason', ''),
        )
        quotation.refresh_from_db()
        return Response(
            QuotationSerializer(quotation).data, status=status.HTTP_200_OK,
        )

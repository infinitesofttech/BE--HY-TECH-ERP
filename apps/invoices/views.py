from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from .models import Invoice, InvoiceItem, Payment
from .serializers import InvoiceSerializer, InvoiceItemSerializer, InvoiceItemCreateSerializer, PaymentSerializer
from . import services
from apps.accounts.permissions import IsManagerOrAbove


class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.prefetch_related('items').all()
    serializer_class = InvoiceSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status']
    search_fields = ['customer_name', 'invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        customer_name = self.request.query_params.get('customer_name')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if customer_name:
            qs = qs.filter(customer_name__icontains=customer_name)
        if date_from:
            qs = qs.filter(invoice_date__gte=date_from)
        if date_to:
            qs = qs.filter(invoice_date__lte=date_to)
        return qs

    @extend_schema(request=InvoiceSerializer, responses={201: InvoiceSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        items_data = self.request.data.get('items', [])
        validated_items = []
        for item in items_data:
            item_ser = InvoiceItemCreateSerializer(data=item)
            item_ser.is_valid(raise_exception=True)
            validated_items.append(item_ser.validated_data)
        serializer.save(created_by=self.request.user, items_data=validated_items)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.prefetch_related('items').all()
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        items_data = request.data.get('items', None)
        validated_items = None
        if items_data is not None:
            validated_items = []
            for item in items_data:
                item_ser = InvoiceItemCreateSerializer(data=item)
                item_ser.is_valid(raise_exception=True)
                validated_items.append(item_ser.validated_data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(items_data=validated_items)
        return Response(serializer.data)

    @extend_schema(request=InvoiceSerializer, responses={200: InvoiceSerializer})
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(request=InvoiceSerializer, responses={200: InvoiceSerializer})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related('invoice').all()
    serializer_class = PaymentSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['invoice', 'method']
    search_fields = ['reference_number', 'notes']
    ordering_fields = ['payment_date', 'amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    @extend_schema(request=PaymentSerializer, responses={201: PaymentSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related('invoice').all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @extend_schema(request=PaymentSerializer, responses={200: PaymentSerializer})
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(request=PaymentSerializer, responses={200: PaymentSerializer})
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class InvoiceMarkPaidView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer

    @extend_schema(responses={200: InvoiceSerializer})
    def post(self, request, pk):
        try:
            invoice = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response(
                {'detail': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            invoice = services.mark_invoice_paid(
                invoice,
                method=request.data.get('method', 'cash'),
                amount=request.data.get('amount'),
                payment_date=request.data.get('payment_date'),
                reference_number=request.data.get('reference_number', ''),
                notes=request.data.get('notes', ''),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.refresh_from_db()
        return Response(
            InvoiceSerializer(invoice).data, status=status.HTTP_200_OK,
        )

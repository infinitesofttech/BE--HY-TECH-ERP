from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Vendor,
    Purchase,
    PurchaseOrder,
    PurchaseReturn,
)
from .serializers import (
    VendorSerializer,
    PurchaseSerializer,
    PurchaseCreateSerializer,
    PurchaseUpdateSerializer,
    PurchaseOrderSerializer,
    PurchaseOrderCreateSerializer,
    PurchaseOrderUpdateSerializer,
    PurchaseReturnSerializer,
    PurchaseReturnCreateSerializer,
    PurchaseReturnUpdateSerializer,
)
from apps.accounts.permissions import IsSuperAdmin, IsManagerOrAbove
from apps.common.utils import parse_date_range


class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'country']
    search_fields = ['name', 'contact_person', 'email', 'phone', 'country']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class PurchaseListCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.select_related(
        'vendor', 'requestor',
    ).prefetch_related('items__product').all()
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['vendor', 'requestor', 'status', 'payment_terms', 'date']
    search_fields = [
        'purchase_id', 'reference', 'vendor__name', 'notes',
    ]
    ordering_fields = ['date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseCreateSerializer
        return PurchaseSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase = serializer.save()
        return Response(
            PurchaseSerializer(purchase).data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.select_related(
        'vendor', 'requestor',
    ).prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PurchaseUpdateSerializer
        return PurchaseSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.select_related(
        'vendor',
    ).prefetch_related('items__product').all()
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = [
        'vendor', 'status', 'payment_terms', 'order_date',
    ]
    search_fields = [
        'purchase_order_id', 'reference', 'vendor__name', 'notes',
    ]
    ordering_fields = ['order_date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            PurchaseOrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.select_related(
        'vendor',
    ).prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PurchaseOrderUpdateSerializer
        return PurchaseOrderSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class PurchaseReturnListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseReturn.objects.select_related(
        'purchase', 'vendor',
    ).prefetch_related('items__product').all()
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = [
        'purchase', 'vendor', 'status', 'return_date',
    ]
    search_fields = [
        'return_id', 'reference', 'vendor__name', 'return_reason',
    ]
    ordering_fields = ['return_date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseReturnCreateSerializer
        return PurchaseReturnSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase_return = serializer.save()
        return Response(
            PurchaseReturnSerializer(purchase_return).data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseReturnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseReturn.objects.select_related(
        'purchase', 'vendor',
    ).prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PurchaseReturnUpdateSerializer
        return PurchaseReturnSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


def rate_on_time_percent(percent):
    if percent is None:
        return None
    if percent >= 90:
        return 'excellent'
    if percent >= 75:
        return 'good'
    if percent >= 60:
        return 'average'
    return 'poor'


class PurchaseAnalyticsView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result

        purchases = Purchase.objects.filter(
            date__gte=start,
            date__lte=end,
        ).select_related('vendor', 'requestor')

        total_spend = purchases.aggregate(
            total=Sum('total_amount'),
        )['total'] or 0
        suppliers = purchases.values('vendor').distinct().count()

        orders = PurchaseOrder.objects.filter(
            order_date__gte=start,
            order_date__lte=end,
        ).select_related('vendor')

        lead_times = [
            (o.actual_delivery_date - o.order_date).days
            for o in orders
            if o.actual_delivery_date
        ]
        avg_lead_time = (
            sum(lead_times) / len(lead_times) if lead_times else None
        )

        delivered = [
            o for o in orders
            if o.actual_delivery_date and o.expected_delivery_date
        ]
        on_time_count = sum(
            1 for o in delivered if o.actual_delivery_date <= o.expected_delivery_date
        )
        on_time_percent = (
            on_time_count / len(delivered) * 100 if delivered else None
        )

        by_vendor = defaultdict(lambda: {
            'total_spend': 0,
            'orders': [],
            'lead_times': [],
            'requestors': set(),
        })
        for purchase in purchases:
            entry = by_vendor[purchase.vendor_id]
            entry['total_spend'] += float(purchase.total_amount)
            if purchase.requestor_id:
                entry['requestors'].add(purchase.requestor_id)

        for order in orders:
            entry = by_vendor[order.vendor_id]
            entry['orders'].append(order)
            if order.actual_delivery_date:
                entry['lead_times'].append(
                    (order.actual_delivery_date - order.order_date).days,
                )

        vendors = {
            v.id: v for v in
            Vendor.objects.filter(id__in=list(by_vendor.keys()))
        }
        User = get_user_model()
        users = {
            u.id: u for u in
            User.objects.filter(id__in=[
                rid for entry in by_vendor.values() for rid in entry['requestors']
            ])
        }
        records = []
        for vendor_id, entry in by_vendor.items():
            vendor = vendors.get(vendor_id)
            lead_times = entry['lead_times']
            vendor_avg_lead_time = (
                sum(lead_times) / len(lead_times) if lead_times else None
            )
            vendor_delivered = [
                o for o in entry['orders']
                if o.actual_delivery_date and o.expected_delivery_date
            ]
            vendor_on_time_count = sum(
                1 for o in vendor_delivered
                if o.actual_delivery_date <= o.expected_delivery_date
            )
            vendor_on_time_percent = (
                vendor_on_time_count / len(vendor_delivered) * 100
                if vendor_delivered else None
            )
            requestors = []
            for rid in sorted(entry['requestors']):
                user = users.get(rid)
                if user:
                    requestors.append(user.get_full_name() or user.email)
                else:
                    requestors.append(str(rid))
            records.append({
                'vendor_id': vendor_id,
                'vendor': vendor.name if vendor else 'N/A',
                'requestors': requestors,
                'total_spend': round(entry['total_spend'], 2),
                'avg_lead_time_days': (
                    round(vendor_avg_lead_time, 2)
                    if vendor_avg_lead_time is not None else None
                ),
                'on_time_percent': (
                    round(vendor_on_time_percent, 2)
                    if vendor_on_time_percent is not None else None
                ),
                'status': rate_on_time_percent(vendor_on_time_percent),
            })
        records.sort(key=lambda r: r['total_spend'], reverse=True)

        return Response({
            'date_from': str(start),
            'date_to': str(end),
            'total_spend': float(total_spend),
            'suppliers': suppliers,
            'avg_lead_time_days': (
                round(avg_lead_time, 2)
                if avg_lead_time is not None else None
            ),
            'on_time_percent': (
                round(on_time_percent, 2)
                if on_time_percent is not None else None
            ),
            'status': rate_on_time_percent(on_time_percent),
            'records': records,
        }, status=status.HTTP_200_OK)

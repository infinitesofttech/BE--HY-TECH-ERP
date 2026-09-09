from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, F
from django.http import HttpResponse
from datetime import datetime, timedelta
import openpyxl
from .models import (
    Customer, SalesOrder, SalesOrderItem,
    Refund, DeliveryNote, CustomerFeedback,
)
from .serializers import (
    CustomerSerializer,
    CustomerFeedbackSerializer,
    SalesOrderSerializer,
    SalesOrderCreateSerializer,
    SalesOrderUpdateSerializer,
    RefundSerializer,
    DeliveryNoteSerializer,
    DeliveryNoteCreateSerializer,
    DeliveryNoteUpdateSerializer,
)
from apps.accounts.permissions import IsSuperAdmin, IsManagerOrAbove
from apps.common.utils import parse_date_range


def compute_sales_overview(start, end):
    window_len = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=window_len - 1)

    orders = SalesOrder.objects.filter(
        status__in=['in_progress', 'completed'],
        date__gte=start,
        date__lte=end,
    )
    prev_orders = SalesOrder.objects.filter(
        status__in=['in_progress', 'completed'],
        date__gte=prev_start,
        date__lte=prev_end,
    )

    total_orders = orders.count()
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    completed_orders = orders.filter(status='completed').count()

    avg_order_value = total_sales / total_orders if total_orders else 0
    conversion_rate = completed_orders / total_orders * 100 if total_orders else 0

    prev_total_orders = prev_orders.count()
    prev_total_sales = prev_orders.aggregate(
        total=Sum('total_amount'),
    )['total'] or 0
    prev_completed_orders = prev_orders.filter(status='completed').count()

    prev_avg_order_value = (
        prev_total_sales / prev_total_orders if prev_total_orders else 0
    )
    prev_conversion_rate = (
        prev_completed_orders / prev_total_orders * 100
        if prev_total_orders else 0
    )

    def pct_change(current, previous):
        if previous:
            return round(
                (current - previous) / previous * 100,
                2,
            )
        return None

    def build_product_data(queryset):
        data = {}
        for item in queryset.select_related('product__category'):
            pid = item.product_id
            if pid not in data:
                data[pid] = {
                    'product_id': pid,
                    'product_name': item.product.name,
                    'category': (
                        item.product.category.name
                        if item.product.category else None
                    ),
                    'unit_price': float(item.unit_price),
                    'unit_sold': 0,
                    'revenue': 0.0,
                }
            data[pid]['unit_sold'] += item.quantity
            data[pid]['revenue'] += float(item.amount + item.tax_amount)
        return data

    current = build_product_data(
        SalesOrderItem.objects.filter(order__in=orders),
    )
    previous = build_product_data(
        SalesOrderItem.objects.filter(order__in=prev_orders),
    )

    products = []
    for pid, item in current.items():
        prev_revenue = previous.get(pid, {}).get('revenue', 0.0)
        if prev_revenue:
            growth = (item['revenue'] - prev_revenue) / prev_revenue * 100
        elif item['revenue']:
            growth = None
        else:
            growth = 0
        products.append({**item, 'growth': growth})

    return {
        'date_from': str(start),
        'date_to': str(end),
        'total_sales': float(total_sales),
        'total_sales_growth': pct_change(total_sales, prev_total_sales),
        'total_orders': total_orders,
        'total_orders_growth': pct_change(total_orders, prev_total_orders),
        'avg_order_value': round(float(avg_order_value), 2),
        'avg_order_value_growth': pct_change(
            avg_order_value, prev_avg_order_value,
        ),
        'conversion_rate': round(float(conversion_rate), 2),
        'conversion_rate_growth': pct_change(
            conversion_rate, prev_conversion_rate,
        ),
        'products': products,
    }


class SalesReportListView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result
        return Response(
            compute_sales_overview(start, end),
            status=status.HTTP_200_OK,
        )


class SalesReportDetailView(generics.RetrieveAPIView):
    queryset = SalesOrder.objects.select_related(
        'employee', 'customer',
    ).prefetch_related('items__product').all()
    serializer_class = SalesOrderSerializer


class DailySalesReportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            report_date = datetime.now().date()

        orders = SalesOrder.objects.filter(
            date=report_date,
            status__in=['in_progress', 'completed'],
        ).select_related('employee')

        aggregated = orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
        )

        employee_data = {}
        for order in orders:
            emp_id = order.employee_id
            if emp_id is None:
                continue
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    'employee_id': emp_id,
                    'employee_name': (
                        order.employee.get_full_name() or order.employee.email
                    ),
                    'total_revenue': 0,
                    'total_orders': 0,
                }
            employee_data[emp_id]['total_revenue'] += float(order.total_amount)
            employee_data[emp_id]['total_orders'] += 1

        return Response({
            'date': report_date,
            'total_revenue': float(aggregated['total_revenue'] or 0),
            'total_orders': aggregated['total_orders'] or 0,
            'employees': list(employee_data.values()),
        }, status=status.HTTP_200_OK)


class MonthlySalesReportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        year = request.query_params.get('year', datetime.now().year)
        month = request.query_params.get('month', datetime.now().month)

        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid year or month.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        orders = SalesOrder.objects.filter(
            date__year=year,
            date__month=month,
            status__in=['in_progress', 'completed'],
        ).select_related('employee')

        employee_data = {}
        for order in orders:
            emp_id = order.employee_id
            if emp_id is None:
                continue
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    'employee_id': emp_id,
                    'employee_name': (
                        order.employee.get_full_name() or order.employee.email
                    ),
                    'total_revenue': 0,
                    'total_orders': 0,
                }
            employee_data[emp_id]['total_revenue'] += float(order.total_amount)
            employee_data[emp_id]['total_orders'] += 1

        total_aggregate = orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
        )

        return Response({
            'year': year,
            'month': month,
            'total_revenue': float(total_aggregate['total_revenue'] or 0),
            'total_orders': total_aggregate['total_orders'] or 0,
            'employees': list(employee_data.values()),
        }, status=status.HTTP_200_OK)


class EmployeeSalesView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request, employee_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            employee = User.objects.get(pk=employee_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Employee not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        orders = SalesOrder.objects.filter(
            employee=employee,
            status__in=['in_progress', 'completed'],
        ).select_related('customer').prefetch_related('items__product')

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            orders = orders.filter(date__gte=date_from)
        if date_to:
            orders = orders.filter(date__lte=date_to)

        aggregated = orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
        )

        return Response({
            'employee_id': employee_id,
            'employee_name': employee.get_full_name() or employee.email,
            'total_revenue': float(aggregated['total_revenue'] or 0),
            'total_orders': aggregated['total_orders'] or 0,
            'orders': SalesOrderSerializer(orders, many=True).data,
        }, status=status.HTTP_200_OK)


class SalesExportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        orders = SalesOrder.objects.select_related(
            'employee', 'customer',
        ).prefetch_related('items__product').all()

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            orders = orders.filter(date__gte=date_from)
        if date_to:
            orders = orders.filter(date__lte=date_to)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Sales Report'

        headers = [
            'Order ID', 'Employee', 'Customer', 'Date', 'Status',
            'Payment Method', 'Total Amount', 'Notes', 'Created At',
        ]
        ws.append(headers)

        for order in orders:
            employee_name = (
                order.employee.get_full_name() or order.employee.email
                if order.employee else 'N/A'
            )
            ws.append([
                order.order_id,
                employee_name,
                order.customer.name,
                order.date.strftime('%Y-%m-%d'),
                order.status,
                order.payment_method,
                float(order.total_amount),
                order.notes,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        ws.append([])
        ws.append(['Items Detail'])
        ws.append([
            'Order ID', 'Product', 'Quantity', 'Unit Price',
            'Amount', 'Tax Amount',
        ])
        for order in orders:
            for item in order.items.select_related('product').all():
                ws.append([
                    order.order_id,
                    item.product.name,
                    item.quantity,
                    float(item.unit_price),
                    float(item.amount),
                    float(item.tax_amount),
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
        filename = f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['country']
    search_fields = ['name', 'email', 'phone', 'country']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class CustomerFeedbackListCreateView(generics.ListCreateAPIView):
    queryset = CustomerFeedback.objects.select_related('customer').all()
    serializer_class = CustomerFeedbackSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['customer', 'status']
    search_fields = ['subject', 'feedback', 'customer__name']
    ordering_fields = ['date', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]


class CustomerFeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerFeedback.objects.select_related('customer').all()
    serializer_class = CustomerFeedbackSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.select_related(
        'customer',
    ).prefetch_related('items__product').all()
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['customer', 'status', 'payment_method', 'date']
    search_fields = ['order_id', 'customer__name', 'notes']
    ordering_fields = ['date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SalesOrderCreateSerializer
        return SalesOrderSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            SalesOrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOrder.objects.select_related(
        'customer',
    ).prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return SalesOrderUpdateSerializer
        return SalesOrderSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class RefundListCreateView(generics.ListCreateAPIView):
    queryset = Refund.objects.select_related('customer').all()
    serializer_class = RefundSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['customer', 'status', 'payment_method']
    search_fields = ['refund_id', 'reference', 'customer__name', 'refund_reason']
    ordering_fields = ['amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class RefundDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Refund.objects.select_related('customer').all()
    serializer_class = RefundSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class DeliveryNoteListCreateView(generics.ListCreateAPIView):
    queryset = DeliveryNote.objects.select_related(
        'customer',
    ).prefetch_related('items__product').all()
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['customer', 'status', 'frequency']
    search_fields = [
        'delivery_note_id', 'reference', 'customer__name',
    ]
    ordering_fields = ['invoice_date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeliveryNoteCreateSerializer
        return DeliveryNoteSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_note = serializer.save()
        return Response(
            DeliveryNoteSerializer(delivery_note).data,
            status=status.HTTP_201_CREATED,
        )


class DeliveryNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeliveryNote.objects.select_related(
        'customer',
    ).prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return DeliveryNoteUpdateSerializer
        return DeliveryNoteSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class DeliveryNoteToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            delivery_note = DeliveryNote.objects.get(pk=pk)
        except DeliveryNote.DoesNotExist:
            return Response(
                {'detail': 'Delivery note not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        delivery_note.status = (
            'inactive' if delivery_note.status == 'active' else 'active'
        )
        delivery_note.save(update_fields=['status'])
        return Response({
            'detail': (
                f'Delivery note {"activated" if delivery_note.status == "active" else "deactivated"} successfully.'
            ),
            'status': delivery_note.status,
        }, status=status.HTTP_200_OK)


class SalesOrderStartProductionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            sales_order = SalesOrder.objects.select_related(
                'customer', 'quotation',
            ).prefetch_related('items__product').get(pk=pk)
        except SalesOrder.DoesNotExist:
            return Response(
                {'detail': 'Sales order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if sales_order.status == 'cancelled':
            return Response(
                {'detail': 'Cannot start production for a cancelled order.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.production import services as production_services
        from apps.production.serializers import JobOrderSerializer

        job_orders = production_services.create_job_orders_from_sales_order(
            sales_order,
            start_date=request.data.get('start_date'),
        )
        return Response({
            'sales_order_id': sales_order.order_id,
            'job_orders': JobOrderSerializer(job_orders, many=True).data,
        }, status=status.HTTP_201_CREATED)


class DeliveryNoteCreateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from apps.invoices.services import create_invoice_from_delivery_note
        from apps.invoices.serializers import InvoiceSerializer

        try:
            delivery_note = DeliveryNote.objects.select_related(
                'customer', 'sales_order',
            ).prefetch_related('items__product').get(pk=pk)
        except DeliveryNote.DoesNotExist:
            return Response(
                {'detail': 'Delivery note not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            invoice = create_invoice_from_delivery_note(
                delivery_note,
                employee=request.user,
                due_in_days=request.data.get('due_in_days', 15),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED,
        )


class SalesAnalysisView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result
        return Response(
            compute_sales_overview(start, end),
            status=status.HTTP_200_OK,
        )

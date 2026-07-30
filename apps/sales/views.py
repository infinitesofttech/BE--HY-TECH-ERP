from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, F
from django.http import HttpResponse
from datetime import datetime
import openpyxl
from .models import SalesReport, SalesReportItem
from .serializers import (
    SalesReportSerializer,
    SalesReportCreateSerializer,
)
from apps.accounts.permissions import IsSuperAdmin, IsManagerOrAbove


class SalesReportCreateView(generics.CreateAPIView):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return Response(
            SalesReportSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )


class SalesReportListView(generics.ListAPIView):
    serializer_class = SalesReportSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['employee', 'dealer', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'notes']
    ordering_fields = ['date', 'total_revenue', 'created_at']

    def get_queryset(self):
        queryset = SalesReport.objects.select_related(
            'employee', 'dealer',
        ).prefetch_related('items__product').all()

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset


class SalesReportDetailView(generics.RetrieveAPIView):
    queryset = SalesReport.objects.select_related(
        'employee', 'dealer',
    ).prefetch_related('items__product').all()
    serializer_class = SalesReportSerializer


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

        reports = SalesReport.objects.filter(
            date=report_date,
        ).select_related('employee', 'dealer').prefetch_related('items__product')

        aggregated = reports.aggregate(
            total_revenue=Sum('total_revenue'),
            total_items=Sum('total_items'),
            report_count=Count('id'),
        )

        employee_data = {}
        for report in reports:
            emp_id = report.employee.id
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    'employee_id': emp_id,
                    'employee_name': report.employee.get_full_name() or report.employee.email,
                    'total_revenue': 0,
                    'total_items': 0,
                    'reports': [],
                }
            employee_data[emp_id]['total_revenue'] += float(report.total_revenue)
            employee_data[emp_id]['total_items'] += report.total_items
            employee_data[emp_id]['reports'].append(
                SalesReportSerializer(report).data,
            )

        return Response({
            'date': report_date,
            'total_revenue': float(aggregated['total_revenue'] or 0),
            'total_items': aggregated['total_items'] or 0,
            'report_count': aggregated['report_count'] or 0,
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

        reports = SalesReport.objects.filter(
            date__year=year,
            date__month=month,
        ).select_related('employee').order_by('employee', '-date')

        employee_data = {}
        for report in reports:
            emp_id = report.employee.id
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    'employee_id': emp_id,
                    'employee_name': report.employee.get_full_name() or report.employee.email,
                    'total_revenue': 0,
                    'total_items': 0,
                    'report_count': 0,
                }
            employee_data[emp_id]['total_revenue'] += float(report.total_revenue)
            employee_data[emp_id]['total_items'] += report.total_items
            employee_data[emp_id]['report_count'] += 1

        total_aggregate = reports.aggregate(
            total_revenue=Sum('total_revenue'),
            total_items=Sum('total_items'),
            report_count=Count('id'),
        )

        return Response({
            'year': year,
            'month': month,
            'total_revenue': float(total_aggregate['total_revenue'] or 0),
            'total_items': total_aggregate['total_items'] or 0,
            'report_count': total_aggregate['report_count'] or 0,
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

        reports = SalesReport.objects.filter(
            employee=employee,
        ).select_related('dealer').prefetch_related('items__product')

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            reports = reports.filter(date__gte=date_from)
        if date_to:
            reports = reports.filter(date__lte=date_to)

        aggregated = reports.aggregate(
            total_revenue=Sum('total_revenue'),
            total_items=Sum('total_items'),
            report_count=Count('id'),
        )

        return Response({
            'employee_id': employee_id,
            'employee_name': employee.get_full_name() or employee.email,
            'total_revenue': float(aggregated['total_revenue'] or 0),
            'total_items': aggregated['total_items'] or 0,
            'report_count': aggregated['report_count'] or 0,
            'reports': SalesReportSerializer(reports, many=True).data,
        }, status=status.HTTP_200_OK)


class SalesExportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        reports = SalesReport.objects.select_related(
            'employee', 'dealer',
        ).prefetch_related('items__product').all()

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            reports = reports.filter(date__gte=date_from)
        if date_to:
            reports = reports.filter(date__lte=date_to)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Sales Report'

        headers = [
            'Report ID', 'Employee', 'Dealer', 'Date',
            'Total Revenue', 'Total Items', 'Notes', 'Created At',
        ]
        ws.append(headers)

        for report in reports:
            ws.append([
                report.id,
                report.employee.get_full_name() or report.employee.email,
                report.dealer.name if report.dealer else 'N/A',
                report.date.strftime('%Y-%m-%d'),
                float(report.total_revenue),
                report.total_items,
                report.notes,
                report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        ws.append([])
        ws.append(['Items Detail'])
        ws.append([
            'Report ID', 'Product', 'Quantity', 'Unit Price', 'Total',
        ])
        for report in reports:
            for item in report.items.select_related('product').all():
                ws.append([
                    report.id,
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
        filename = f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response

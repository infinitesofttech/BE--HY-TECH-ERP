import io
from decimal import Decimal

from django.db.models import Sum, Count, Q, F, DecimalField, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsManagerOrAbove
from .models import Target
from .serializers import (
    TargetSerializer,
    TargetCreateSerializer,
    TargetWithAchievementSerializer,
)


class TargetAssignView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    serializer_class = TargetCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = TargetSerializer(serializer.instance)
        return Response(output.data, status=status.HTTP_201_CREATED)


class TargetListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    serializer_class = TargetWithAchievementSerializer

    def get_queryset(self):
        qs = Target.objects.select_related('employee', 'product').all()
        employee = self.request.query_params.get('employee')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if employee:
            qs = qs.filter(employee_id=employee)
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)
        return qs


class MyTargetsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TargetWithAchievementSerializer

    def get_queryset(self):
        return Target.objects.filter(
            employee=self.request.user
        ).select_related('employee', 'product')


class TargetDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TargetSerializer

    def get_queryset(self):
        if self.request.user.role in ('super_admin', 'manager'):
            return Target.objects.select_related('employee', 'product').all()
        return Target.objects.filter(
            employee=self.request.user
        ).select_related('employee', 'product')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TargetCreateSerializer
        return TargetSerializer


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            return Response(
                {'error': 'month and year query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            month = int(month)
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {'error': 'month and year must be integers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        targets = Target.objects.filter(
            month=month, year=year
        ).values('employee').annotate(
            total_target=Coalesce(Sum('target_amount'), Value(0, output_field=DecimalField())),
        )

        leaderboard = []

        for entry in targets:
            employee_id = entry['employee']
            total_target = entry['total_target']

            achieved = Decimal('0')
            total_visits = 0
            total_distance = Decimal('0')

            from apps.sales.models import SalesReport, SalesReportItem

            sales_qs = SalesReport.objects.filter(
                employee_id=employee_id,
                date__year=year,
                date__month=month,
            )
            achieved_result = sales_qs.aggregate(total=Sum('total_revenue'))
            if achieved_result['total']:
                achieved = achieved_result['total']

            try:
                from apps.visits.models import Visit
                total_visits = Visit.objects.filter(
                    employee_id=employee_id,
                    check_in_time__year=year,
                    check_in_time__month=month,
                ).count()
            except (ImportError, LookupError):
                pass

            try:
                from apps.tracking.models import TrackingLocation
                tracking_count = TrackingLocation.objects.filter(
                    employee_id=employee_id,
                    timestamp__year=year,
                    timestamp__month=month,
                ).count()
                total_distance = Decimal(str(tracking_count * 0.5))
            except (ImportError, LookupError):
                pass

            achievement_pct = 0
            if total_target > 0:
                achievement_pct = round(float(achieved / total_target) * 100, 2)

            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                employee = User.objects.get(pk=employee_id)
                employee_name = employee.get_full_name() or employee.email
            except Exception:
                employee_name = str(employee_id)

            leaderboard.append({
                'employee': employee_id,
                'employee_name': employee_name,
                'target': float(total_target),
                'achieved': float(achieved),
                'achievement_percentage': achievement_pct,
                'total_visits': total_visits,
                'total_distance': float(total_distance),
            })

        leaderboard.sort(key=lambda x: x['achievement_percentage'], reverse=True)

        for rank, entry in enumerate(leaderboard, start=1):
            entry['rank'] = rank

        return Response(leaderboard)


class TargetExportView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        targets = Target.objects.select_related('employee', 'product').all()

        employee = request.query_params.get('employee')
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if employee:
            targets = targets.filter(employee_id=employee)
        if month:
            targets = targets.filter(month=month)
        if year:
            targets = targets.filter(year=year)

        try:
            import openpyxl
        except ImportError:
            return Response(
                {'error': 'openpyxl is required for Excel export.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Targets'

        headers = [
            'ID', 'Employee', 'Email', 'Month', 'Year',
            'Target Amount', 'Product', 'Notes', 'Created At',
        ]
        ws.append(headers)

        for target in targets:
            ws.append([
                target.id,
                target.employee.get_full_name() or target.employee.email,
                target.employee.email,
                target.month,
                target.year,
                float(target.target_amount),
                target.product.name if target.product else '',
                target.notes,
                target.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="targets.xlsx"'
        return response

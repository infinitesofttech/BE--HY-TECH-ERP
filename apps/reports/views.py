from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Count, Q, F, DecimalField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from apps.accounts.permissions import IsManagerOrAbove
from .serializers import (
    DashboardSerializer,
    EmployeePerformanceSerializer,
    CompareSerializer,
    WeakAreaSerializer,
)
from .utils import (
    get_date_range,
    aggregate_employee_sales,
    aggregate_employee_visits,
    aggregate_employee_attendance,
    aggregate_employee_distance,
    aggregate_employee_targets,
)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        now = timezone.localtime()
        today = now.date()

        total_employees = User.objects.filter(
            role__in=['msr', 'manager'],
        ).count()
        active_employees = User.objects.filter(
            role__in=['msr', 'manager'],
            is_active=True,
        ).count()

        today_attendance = 0
        try:
            from apps.attendance.models import Attendance
            today_attendance = Attendance.objects.filter(
                date=today,
            ).count()
        except (ImportError, LookupError):
            pass

        online_employees = 0
        try:
            from apps.tracking.models import TrackingLocation
            five_min_ago = now - timedelta(minutes=5)
            recent_employee_ids = TrackingLocation.objects.filter(
                timestamp__gte=five_min_ago,
            ).values_list('employee_id', flat=True).distinct()
            online_employees = User.objects.filter(
                role__in=['msr', 'manager'],
                is_active=True,
                id__in=recent_employee_ids,
            ).count()
        except (ImportError, LookupError):
            pass

        total_dealers = 0
        try:
            from apps.masters.models import Dealer
            total_dealers = Dealer.objects.count()
        except (ImportError, LookupError):
            pass

        total_retailers = 0
        try:
            from apps.masters.models import Retailer
            total_retailers = Retailer.objects.count()
        except (ImportError, LookupError):
            pass

        total_mechanics = 0
        try:
            from apps.masters.models import Mechanic
            total_mechanics = Mechanic.objects.count()
        except (ImportError, LookupError):
            pass

        total_sales_this_month = 0
        try:
            from apps.sales.models import SalesReport
            result = SalesReport.objects.filter(
                date__year=today.year,
                date__month=today.month,
            ).aggregate(total=Coalesce(
                Sum('total_revenue'),
                Value(0, output_field=DecimalField()),
            ))
            total_sales_this_month = result['total']
        except (ImportError, LookupError):
            pass

        pending_leaves = 0
        try:
            from apps.leaves.models import Leave
            pending_leaves = Leave.objects.filter(
                status='pending',
            ).count()
        except (ImportError, LookupError):
            pass

        unread_notifications = 0
        try:
            from apps.notifications.models import NotificationRecipient
            unread_notifications = NotificationRecipient.objects.filter(
                recipient=request.user,
                is_read=False,
            ).count()
        except (ImportError, LookupError):
            pass

        data = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'today_attendance': today_attendance,
            'online_employees': online_employees,
            'total_dealers': total_dealers,
            'total_retailers': total_retailers,
            'total_mechanics': total_mechanics,
            'total_sales_this_month': total_sales_this_month,
            'pending_leaves': pending_leaves,
            'unread_notifications': unread_notifications,
        }

        serializer = DashboardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PerformanceOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            year = int(request.query_params.get('year', timezone.localtime().year))
            month = int(request.query_params.get('month', timezone.localtime().month))
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid year or month.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        territory = request.query_params.get('territory')
        pin_code = request.query_params.get('pin_code')

        employees = User.objects.filter(
            role='msr',
            is_active=True,
        )
        if territory:
            employees = employees.filter(territory=territory)
        if pin_code:
            employees = employees.filter(pin_code=pin_code)

        start_date, end_date = get_date_range(year, month)

        performance_data = []
        for emp in employees:
            total_sales = aggregate_employee_sales(emp.id, start_date, end_date)
            total_visits = aggregate_employee_visits(emp.id, start_date, end_date)
            attendance = aggregate_employee_attendance(emp.id, start_date, end_date)
            total_distance = aggregate_employee_distance(emp.id, start_date, end_date)
            targets = aggregate_employee_targets(emp.id, start_date, end_date)

            performance_data.append({
                'employee_id': emp.id,
                'employee_name': emp.get_full_name() or emp.email,
                'email': emp.email,
                'territory': emp.territory,
                'pin_code': emp.pin_code,
                'total_sales': total_sales,
                'total_visits': total_visits,
                'attendance_days': attendance['present_days'],
                'total_calendar_days': attendance['total_days'],
                'attendance_percentage': attendance['attendance_percentage'],
                'total_distance': total_distance,
                'total_target': targets['total_target'],
                'target_achievement_percentage': targets['achievement_percentage'],
            })

        serializer = EmployeePerformanceSerializer(performance_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompareEmployeesView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        employee_a_id = request.query_params.get('employee_a')
        employee_b_id = request.query_params.get('employee_b')

        if not employee_a_id or not employee_b_id:
            return Response(
                {'detail': 'employee_a and employee_b query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year = int(request.query_params.get('year', timezone.localtime().year))
            month = int(request.query_params.get('month', timezone.localtime().month))
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid year or month.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            emp_a = User.objects.get(pk=employee_a_id)
            emp_b = User.objects.get(pk=employee_b_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'One or both employees not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        start_date, end_date = get_date_range(year, month)

        def build_metrics(emp):
            total_sales = aggregate_employee_sales(emp.id, start_date, end_date)
            total_visits = aggregate_employee_visits(emp.id, start_date, end_date)
            attendance = aggregate_employee_attendance(emp.id, start_date, end_date)
            total_distance = aggregate_employee_distance(emp.id, start_date, end_date)
            targets = aggregate_employee_targets(emp.id, start_date, end_date)
            return {
                'employee_id': emp.id,
                'employee_name': emp.get_full_name() or emp.email,
                'total_sales': total_sales,
                'total_visits': total_visits,
                'attendance_percentage': attendance['attendance_percentage'],
                'total_distance': total_distance,
                'total_target': targets['total_target'],
                'target_achievement_percentage': targets['achievement_percentage'],
            }

        data = {
            'employee_a': build_metrics(emp_a),
            'employee_b': build_metrics(emp_b),
        }

        serializer = CompareSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeakAreaAnalysisView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            year = int(request.query_params.get('year', timezone.localtime().year))
            month = int(request.query_params.get('month', timezone.localtime().month))
        except (ValueError, TypeError):
            return Response(
                {'detail': 'Invalid year or month.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_date, end_date = get_date_range(year, month)

        employees = User.objects.filter(
            role='msr',
            is_active=True,
        ).exclude(territory='')

        territory_data = {}
        for emp in employees:
            territory = emp.territory or 'Unknown'
            pin_code = emp.pin_code or ''
            key = territory
            if key not in territory_data:
                territory_data[key] = {
                    'territory': territory,
                    'pin_code': pin_code,
                    'employees': [],
                    'total_sales': 0,
                    'total_visits': 0,
                    'employee_count': 0,
                }
            territory_data[key]['employees'].append(emp)
            territory_data[key]['employee_count'] += 1

            sales = aggregate_employee_sales(emp.id, start_date, end_date)
            visits = aggregate_employee_visits(emp.id, start_date, end_date)
            territory_data[key]['total_sales'] += sales
            territory_data[key]['total_visits'] += visits

        weak_dealers_count = 0
        try:
            from apps.masters.models import Dealer
            weak_dealers_count = Dealer.objects.filter(
                status='inactive',
            ).count()
        except (ImportError, LookupError):
            pass

        total_sales_all = sum(d['total_sales'] for d in territory_data.values())
        total_employees_all = sum(d['employee_count'] for d in territory_data.values())
        avg_sales = 0
        if total_employees_all > 0:
            avg_sales = total_sales_all / total_employees_all

        weak_areas = []
        for key, data in territory_data.items():
            emp_count = data['employee_count']
            total_territory_sales = data['total_sales']
            avg_territory_sales = 0
            if emp_count > 0:
                avg_territory_sales = total_territory_sales / emp_count

            recommendations = []
            is_weak = False

            if avg_territory_sales < avg_sales:
                recommendations.append(
                    f'Average sales ({avg_territory_sales:.2f}) is below overall average ({avg_sales:.2f}). '
                    'Focus on increasing dealer engagement and product promotion.',
                )
                is_weak = True

            if data['total_visits'] == 0:
                recommendations.append(
                    'No visits recorded in this area. Ensure field coverage is planned.',
                )
                is_weak = True

            target_missed = False
            for emp in data['employees']:
                targets = aggregate_employee_targets(emp.id, start_date, end_date)
                if targets['total_target'] > 0 and targets['achievement_percentage'] < 100:
                    target_missed = True
                    break

            if target_missed:
                recommendations.append(
                    'One or more employees missed their targets. '
                    'Review target allocation and provide additional support.',
                )
                is_weak = True

            if is_weak:
                weak_areas.append({
                    'territory': data['territory'],
                    'pin_code': data['pin_code'],
                    'total_sales': data['total_sales'],
                    'total_visits': data['total_visits'],
                    'employee_count': data['employee_count'],
                    'avg_sales_per_employee': round(avg_territory_sales, 2),
                    'weak_dealers_count': weak_dealers_count,
                    'target_missed': target_missed,
                    'recommendations': recommendations,
                })

        serializer = WeakAreaSerializer(weak_areas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

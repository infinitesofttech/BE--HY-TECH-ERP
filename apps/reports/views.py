from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
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
    LeadReportSerializer,
    DealReportSerializer,
    ContactReportSerializer,
    CompanyReportSerializer,
    RevenueReportSerializer,
    ProjectReportSerializer,
    TaskReportSerializer,
    AttendanceReportSerializer,
    LeaveReportSerializer,
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

        total_sales_this_month = 0
        try:
            from apps.sales.models import SalesOrder
            result = SalesOrder.objects.filter(
                date__year=today.year,
                date__month=today.month,
                status__in=['in_progress', 'completed'],
            ).aggregate(total=Coalesce(
                Sum('total_amount'),
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


class LeadReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=LeadReportSerializer(many=True))
    def get(self, request):
        from apps.pipeline.models import Lead
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        source = request.query_params.get('source')
        owner = request.query_params.get('owner')

        qs = Lead.objects.select_related('owner', 'source').all()
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if source:
            qs = qs.filter(source_id=source)
        if owner:
            qs = qs.filter(owner_id=owner)

        data = [{
            'lead_id': lead.id,
            'lead_name': lead.name,
            'company_name': lead.company_name,
            'phone': lead.phone,
            'lead_status': lead.get_status_display(),
            'created_date': lead.created_at.date(),
            'lead_owner': lead.owner.email if lead.owner else None,
        } for lead in qs]

        serializer = LeadReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DealReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DealReportSerializer(many=True))
    def get(self, request):
        from apps.pipeline.models import Deal
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        stage = request.query_params.get('stage') or request.query_params.get('progress')

        qs = Deal.objects.select_related('owner', 'pipeline_stage').all()
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if stage:
            qs = qs.filter(progress=stage)

        data = [{
            'deal_id': deal.id,
            'deal_name': deal.name,
            'stage': deal.get_progress_display(),
            'progress': deal.get_progress_display(),
            'deal_value': deal.value,
            'tags': deal.tags,
            'expected_close_date': deal.expected_close_date,
            'probability': deal.probability,
            'status': deal.get_status_display(),
        } for deal in qs]

        serializer = DealReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContactReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ContactReportSerializer(many=True))
    def get(self, request):
        from apps.contacts.models import Contact
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        source = request.query_params.get('source')

        qs = Contact.objects.select_related('company').all()
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if source:
            qs = qs.filter(source_id=source)

        data = [{
            'contact_id': contact.id,
            'name': contact.name,
            'phone': contact.phone,
            'tags': contact.tags,
            'location': ', '.join(filter(None, [contact.city, contact.state, contact.country])),
            'rating': contact.reviews or '',
            'contact': contact.email,
            'status': contact.get_status_display(),
        } for contact in qs]

        serializer = ContactReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CompanyReportSerializer(many=True))
    def get(self, request):
        from apps.contacts.models import Company
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        owner = request.query_params.get('owner')

        qs = Company.objects.select_related('owner').all()
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if owner:
            qs = qs.filter(owner_id=owner)

        data = [{
            'company_id': company.id,
            'name': company.name,
            'email': company.email,
            'tags': company.tags,
            'owner': company.owner.email if company.owner else None,
            'contact': company.phone,
            'status': company.get_status_display(),
        } for company in qs]

        serializer = CompanyReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RevenueReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=RevenueReportSerializer(many=True))
    def get(self, request):
        from apps.invoices.models import Invoice
        from django.db.models.functions import TruncMonth
        from django.db.models import Sum

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        qs = Invoice.objects.filter(status='paid')
        if date_from:
            qs = qs.filter(invoice_date__gte=date_from)
        if date_to:
            qs = qs.filter(invoice_date__lte=date_to)

        if not qs.exists():
            return Response([], status=status.HTTP_200_OK)

        monthly = (
            qs.annotate(month=TruncMonth('invoice_date'))
            .values('month')
            .annotate(
                total_revenue=Sum('total'),
                invoice_count=Count('id'),
            )
            .order_by('month')
        )

        customer_first_month = {}
        for inv in qs.values('customer_name', 'invoice_date', 'total'):
            month_key = inv['invoice_date'].strftime('%Y-%m')
            if inv['customer_name'] not in customer_first_month:
                customer_first_month[inv['customer_name']] = month_key

        data = []
        prev_total = None
        for row in monthly:
            month = row['month']
            period = month.strftime('%Y-%m')
            total = row['total_revenue'] or 0

            new_revenue = 0
            expansion_revenue = 0
            for inv in qs.filter(invoice_date__year=month.year, invoice_date__month=month.month):
                if customer_first_month.get(inv.customer_name) == period:
                    new_revenue += inv.total or 0
                else:
                    expansion_revenue += inv.total or 0

            mrr = total
            arr = mrr * 12

            growth = None
            if prev_total and prev_total != 0:
                growth = round(((float(total) - float(prev_total)) / float(prev_total)) * 100, 2)

            cancelled = Invoice.objects.filter(
                status='cancelled',
                invoice_date__year=month.year,
                invoice_date__month=month.month,
            ).aggregate(total=Sum('total'))['total'] or 0
            churn_impact = 0.0
            if total > 0:
                churn_impact = round(float(cancelled) / float(total) * 100, 2)

            data.append({
                'period': period,
                'total_revenue': total,
                'new_revenue': new_revenue,
                'expansion_revenue': expansion_revenue,
                'mrr': mrr,
                'arr': arr,
                'growth': growth,
                'churn_impact': churn_impact,
            })
            prev_total = total

        serializer = RevenueReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ProjectReportSerializer(many=True))
    def get(self, request):
        from apps.projects.models import Project
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        priority = request.query_params.get('priority')

        qs = Project.objects.all()
        if date_from:
            qs = qs.filter(start_date__gte=date_from)
        if date_to:
            qs = qs.filter(due_date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority:
            qs = qs.filter(priority=priority)

        data = [{
            'project_id': project.id,
            'name': project.name,
            'client': project.client_name,
            'priority': project.get_priority_display(),
            'start_date': project.start_date,
            'end_date': project.due_date,
            'pipeline_stage': ', '.join(
                d.pipeline_stage.name for d in project.deals.all() if d.pipeline_stage
            ),
            'status': project.get_status_display(),
        } for project in qs.prefetch_related('deals__pipeline_stage')]

        serializer = ProjectReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=TaskReportSerializer(many=True))
    def get(self, request):
        from apps.projects.models import Task
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')
        category = request.query_params.get('category')
        assignee = request.query_params.get('assignee')

        qs = Task.objects.prefetch_related('assignees').all()
        if date_from:
            qs = qs.filter(due_date__gte=date_from)
        if date_to:
            qs = qs.filter(due_date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if category:
            qs = qs.filter(category=category)
        if assignee:
            qs = qs.filter(assignees__id=assignee)

        data = [{
            'task_id': task.id,
            'title': task.title,
            'category': task.get_category_display(),
            'status': task.get_status_display(),
            'priority': task.get_priority_display(),
            'tags': task.tags,
            'due_date': task.due_date,
            'assignees': [u.email for u in task.assignees.all()],
        } for task in qs]

        serializer = TaskReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AttendanceReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AttendanceReportSerializer(many=True))
    def get(self, request):
        from apps.attendance.models import Attendance
        from django.contrib.auth import get_user_model
        User = get_user_model()

        year = request.query_params.get('year')
        month = request.query_params.get('month')
        employee = request.query_params.get('employee')

        qs = Attendance.objects.select_related('employee').all()
        if year:
            qs = qs.filter(date__year=year)
        if month:
            qs = qs.filter(date__month=month)
        if employee:
            qs = qs.filter(employee_id=employee)

        records = list(qs)
        if not records:
            return Response([], status=status.HTTP_200_OK)

        grouped = {}
        for rec in records:
            key = (rec.employee_id, rec.date.strftime('%Y-%m'))
            grouped.setdefault(key, {
                'employee_id': rec.employee_id,
                'employee_name': rec.employee.get_full_name() or rec.employee.email,
                'period': rec.date.strftime('%Y-%m'),
                'total_working_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'late_entries': 0,
                'hours': [],
            })
            entry = grouped[key]
            entry['total_working_days'] += 1
            if rec.status == 'present':
                entry['present_days'] += 1
            elif rec.status == 'absent':
                entry['absent_days'] += 1
            elif rec.status == 'late':
                entry['late_entries'] += 1
            entry['hours'].append(float(rec.total_hours))

        data = []
        for entry in grouped.values():
            avg_hours = 0
            if entry['hours']:
                avg_hours = round(sum(entry['hours']) / len(entry['hours']), 2)
            attendance_rate = 0.0
            if entry['total_working_days'] > 0:
                attendance_rate = round(
                    (entry['present_days'] / entry['total_working_days']) * 100, 2,
                )
            data.append({
                'employee_id': entry['employee_id'],
                'employee_name': entry['employee_name'],
                'period': entry['period'],
                'total_working_days': entry['total_working_days'],
                'present_days': entry['present_days'],
                'absent_days': entry['absent_days'],
                'late_entries': entry['late_entries'],
                'average_work_hours': avg_hours,
                'attendance_rate': attendance_rate,
            })

        serializer = AttendanceReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LeaveReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=LeaveReportSerializer(many=True))
    def get(self, request):
        from apps.leaves.models import LeaveType, LeaveAllocation, Leave
        from django.contrib.auth import get_user_model

        year = request.query_params.get('year')
        employee = request.query_params.get('employee')
        if year:
            try:
                year = int(year)
            except (TypeError, ValueError):
                return Response(
                    {'detail': 'Invalid year.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        data = []
        for leave_type in LeaveType.objects.all():
            allocations = LeaveAllocation.objects.filter(leave_type=leave_type)
            if year:
                allocations = allocations.filter(year=year)
            if employee:
                allocations = allocations.filter(employee_id=employee)
            allocated = sum(a.allotted_days for a in allocations)

            leaves = Leave.objects.filter(leave_type=leave_type)
            if year:
                leaves = leaves.filter(start_date__year=year)
            if employee:
                leaves = leaves.filter(employee_id=employee)

            used = sum(
                l.total_days for l in leaves.filter(status='approved')
            )
            pending = sum(
                l.total_days for l in leaves.filter(status='pending')
            )
            remaining = allocated - used
            utilization = 0.0
            if allocated > 0:
                utilization = round((used / allocated) * 100, 2)

            data.append({
                'leave_type': leave_type.name,
                'allocated': allocated,
                'remaining': remaining,
                'used': used,
                'pending': pending,
                'utilization': utilization,
            })

        serializer = LeaveReportSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.sales.models import Customer, SalesOrder

        now = timezone.localdate()
        month_start = now.replace(day=1)
        prev_month_end = month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        orders = SalesOrder.objects.exclude(status='cancelled')

        total_customers = Customer.objects.count()
        new_this_month = Customer.objects.filter(
            created_at__date__gte=month_start,
        ).count()

        customer_agg = orders.values('customer_id').annotate(
            revenue=Coalesce(
                Sum('total_amount'), Value(0, output_field=DecimalField()),
            ),
            order_count=Count('id'),
        )
        total_revenue = sum(r['revenue'] for r in customer_agg)
        total_orders = sum(r['order_count'] for r in customer_agg)
        repeat_customers = sum(
            1 for r in customer_agg if r['order_count'] >= 2
        )

        retention_ratio = round(
            (repeat_customers / total_customers) * 100, 2,
        ) if total_customers else 0
        avg_ltv = round(total_revenue / total_customers, 2) if total_customers else 0

        segment_customers = Customer.objects.values('country').annotate(
            customers=Count('id'),
        )
        segment_rev = orders.values('customer__country').annotate(
            revenue=Coalesce(
                Sum('total_amount'), Value(0, output_field=DecimalField()),
            ),
            order_count=Count('id'),
        )
        rev_map = {
            r['customer__country']: r for r in segment_rev
        }
        this_month = orders.filter(date__gte=month_start).values(
            'customer__country',
        ).annotate(revenue=Sum('total_amount'))
        last_month = orders.filter(
            date__gte=prev_month_start, date__lt=month_start,
        ).values('customer__country').annotate(revenue=Sum('total_amount'))
        this_map = {r['customer__country']: r['revenue'] or 0 for r in this_month}
        last_map = {r['customer__country']: r['revenue'] or 0 for r in last_month}

        top_segments = []
        for seg in segment_customers.order_by('-customers'):
            country = seg['country'] or 'Unknown'
            rev_data = rev_map.get(seg['country'], {'revenue': 0, 'order_count': 0})
            revenue = rev_data['revenue'] or 0
            order_count = rev_data['order_count'] or 0
            growth = 0.0
            last = last_map.get(seg['country'], 0)
            this = this_map.get(seg['country'], 0)
            if last:
                growth = round(((this - last) / last) * 100, 2)
            elif this:
                growth = 100.0
            top_segments.append({
                'segment': country,
                'customers': seg['customers'],
                'revenue': float(revenue),
                'avg_order': round(revenue / order_count, 2) if order_count else 0,
                'growth': growth,
            })

        return Response({
            'total_customers': total_customers,
            'new_this_month': new_this_month,
            'retention_ratio': retention_ratio,
            'avg_ltv': avg_ltv,
            'top_customer_segments': top_segments,
        }, status=status.HTTP_200_OK)

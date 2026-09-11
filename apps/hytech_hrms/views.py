import calendar
from datetime import date, timedelta, datetime

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    AttendanceRecord, LeaveRecord, LeaveBalance, HolidayItem,
    HRCompanySetting, HRAttendanceSetting, HRLeaveSetting,
    HRNotificationSetting, HRRolePermission
)
from .serializers import (
    AttendanceRecordSerializer, LeaveRecordSerializer,
    LeaveBalanceSerializer, HolidayItemSerializer,
    HRCompanySettingSerializer, HRAttendanceSettingSerializer,
    HRLeaveSettingSerializer, HRNotificationSettingSerializer,
    HRRolePermissionSerializer, HRAllSettingsSerializer
)
from apps.payroll.models import Payroll

User = get_user_model()

STANDARD_WORK_HOURS = 8.0

SHIFT_START = "09:30 AM"
SHIFT_END = "06:30 PM"
SHIFT_START_MINUTE = 9 * 60 + 30


def _get_attendance_config():
    try:
        cfg = HRAttendanceSetting.load()
        shift_start = cfg.shift_start_time or "09:30 AM"
        shift_end = cfg.shift_end_time or "06:30 PM"
        grace = cfg.grace_period_minutes or 15
        parsed_start = _parse_punch(shift_start)
        start_minute = (parsed_start.hour * 60 + parsed_start.minute) if parsed_start else (9 * 60 + 30)
        return shift_start, shift_end, start_minute, grace
    except Exception:
        return "09:30 AM", "06:30 PM", 9 * 60 + 30, 15



def _parse_punch(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def _time_minutes(value):
    return value.hour * 60 + value.minute


def _parse_month(value):
    try:
        year, month = value.split('-')
        return date(int(year), int(month), 1)
    except (AttributeError, ValueError):
        return None


def _month_last_day(first_day):
    return date(
        first_day.year,
        first_day.month,
        calendar.monthrange(first_day.year, first_day.month)[1],
    )


def _working_days(first_day, last_day):
    holidays = set(
        HolidayItem.objects.filter(date__range=(first_day, last_day))
        .values_list('date', flat=True)
    )
    count = 0
    current = first_day
    while current <= last_day:
        if current.weekday() != 6 and current not in holidays:
            count += 1
        current += timedelta(days=1)
    return count


def _attendance_aggregates(employee, first_day, last_day):
    present_days = 0.0
    leave_days = 0
    total_hours = 0.0
    overtime_hours = 0.0
    attendances = AttendanceRecord.objects.filter(
        employee=employee, date__range=(first_day, last_day)
    )
    for att in attendances:
        hours = att.work_hours or 0.0
        total_hours += hours
        if hours > STANDARD_WORK_HOURS:
            overtime_hours += hours - STANDARD_WORK_HOURS
        if att.status == 'PRESENT':
            present_days += 1
        elif att.status == 'HALF_DAY':
            present_days += 0.5
        elif att.status == 'LEAVE':
            leave_days += 1
    return present_days, leave_days, total_hours, overtime_hours


def _approved_leave_days(employee, first_day, last_day):
    leaves = LeaveRecord.objects.filter(
        employee=employee, status='APPROVED',
        start_date__lte=last_day, end_date__gte=first_day,
    )
    total = 0
    for leave in leaves:
        start = max(leave.start_date, first_day)
        end = min(leave.end_date, last_day)
        total += (end - start).days + 1
    return total


def _rate_status(rate):
    if rate >= 90:
        return 'Optimal'
    if rate >= 75:
        return 'Good'
    if rate >= 60:
        return 'Average'
    return 'Needs Improvement'


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all().select_related('employee')
    serializer_class = AttendanceRecordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        emp_id = self.request.query_params.get('employee_id')
        month = self.request.query_params.get('month') # YYYY-MM
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        if month:
            qs = qs.filter(date__startswith=month)
        return qs

    def create(self, request, *args, **kwargs):
        emp_id = request.data.get('employee_id') or request.data.get('employee')
        employee = None
        if emp_id:
            employee = User.objects.filter(id=emp_id).first()
        if not employee and request.user.is_authenticated:
            employee = request.user

        data = request.data.copy()
        if employee:
            data['employee'] = employee.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        rec = serializer.save()
        return Response({
            'message': 'Attendance marked successfully.',
            'data': AttendanceRecordSerializer(rec).data
        }, status=status.HTTP_201_CREATED)


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = LeaveRecord.objects.all().select_related('employee')
    serializer_class = LeaveRecordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        emp_id = self.request.query_params.get('employee_id')
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        return qs

    def create(self, request, *args, **kwargs):
        emp_id = request.data.get('employee_id') or request.data.get('employee')
        employee = None
        if emp_id:
            employee = User.objects.filter(id=emp_id).first()
        if not employee and request.user.is_authenticated:
            employee = request.user

        data = request.data.copy()
        if employee:
            data['employee'] = employee.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        leave = serializer.save()
        return Response(LeaveRecordSerializer(leave).data, status=status.HTTP_201_CREATED)


class LeaveBalanceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, employee_id):
        bal = LeaveBalance.objects.filter(employee_id=employee_id).first()
        if not bal:
            # Default fallback standard balance
            return Response({
                'casual_total': 12,
                'casual_used': 2,
                'sick_total': 7,
                'sick_used': 1,
                'paid_total': 5,
                'paid_used': 1
            })
        return Response(LeaveBalanceSerializer(bal).data)


class HolidayViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HolidayItem.objects.all()
    serializer_class = HolidayItemSerializer
    permission_classes = [AllowAny]


def _visible_employees(request):
    user = request.user
    if user.is_superuser or user.role in ('admin', 'hr'):
        return User.objects.filter(is_active=True).exclude(role='customer')
    return User.objects.filter(pk=user.pk)


def _scoped_leave_queryset(request, month):
    qs = LeaveRecord.objects.select_related('employee')
    is_manager = request.user.is_superuser or request.user.role in ('admin', 'hr')
    if not is_manager:
        qs = qs.filter(employee_id=request.user.pk)
    else:
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            qs = qs.filter(employee_id=int(employee_id))
    if month:
        qs = qs.filter(start_date__startswith=month)
    return qs


class AttendanceSummaryView(APIView):
    """
    GET /hrms/attendance/summary/?month=YYYY-MM
    Summary: average attendance, total days present, total overtime, approved leaves.
    Employees only see their own figures; admins/HR see figures for all employees.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access attendance reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get('month') or timezone.localdate().strftime('%Y-%m')
        first_day = _parse_month(month)
        if not first_day:
            return Response(
                {'error': 'Invalid month. Use YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        last_day = _month_last_day(first_day)
        working_days = _working_days(first_day, last_day)
        employees = _visible_employees(request)

        total_present = 0.0
        total_overtime = 0.0
        approved_leaves = 0
        rates = []
        for employee in employees:
            present, _, _, overtime = _attendance_aggregates(employee, first_day, last_day)
            total_present += present
            total_overtime += overtime
            approved_leaves += _approved_leave_days(employee, first_day, last_day)
            rates.append(round(present / working_days * 100, 1) if working_days else 0.0)

        return Response({
            'month': month,
            'average_attendance': round(sum(rates) / len(rates), 1) if rates else 0.0,
            'total_days_present': round(total_present, 1),
            'total_overtime_hours': round(total_overtime, 2),
            'approved_leaves': approved_leaves,
        }, status=status.HTTP_200_OK)


class AttendanceReportView(APIView):
    """
    GET /hrms/attendance/report/?month=YYYY-MM&employee_id=ID
    Monthly attendance & working hours report per employee:
    employee_id, employee_name, role, working_days, present, leave, hours, rate, status.
    Employees only see their own data; admins/HR see all employees (optionally filtered by employee_id).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access attendance reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get('month') or timezone.localdate().strftime('%Y-%m')
        first_day = _parse_month(month)
        if not first_day:
            return Response(
                {'error': 'Invalid month. Use YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        last_day = _month_last_day(first_day)
        working_days = _working_days(first_day, last_day)
        employees = _visible_employees(request)

        if request.user.is_superuser or request.user.role in ('admin', 'hr'):
            employee_id = request.query_params.get('employee_id')
            if employee_id:
                try:
                    employees = employees.filter(pk=int(employee_id))
                except (TypeError, ValueError):
                    return Response(
                        {'error': 'Invalid employee_id.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        report = []
        for employee in employees:
            present, leave, hours, overtime = _attendance_aggregates(employee, first_day, last_day)
            rate = round(present / working_days * 100, 1) if working_days else 0.0
            report.append({
                'employee_id': employee.id,
                'employee_name': employee.get_full_name() or employee.username,
                'role': employee.role,
                'working_days': working_days,
                'present': round(present, 1),
                'leave': leave,
                'hours': round(hours, 2),
                'overtime_hours': round(overtime, 2),
                'rate': rate,
                'status': _rate_status(rate),
            })

        return Response({'month': month, 'report': report}, status=status.HTTP_200_OK)


class LeaveSummaryView(APIView):
    """
    GET /hrms/leaves/summary/?month=YYYY-MM[&employee_id=ID]
    Summary: total applications, approved / pending / rejected requests.
    Employees only see their own leave records; admins/HR see all employees.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access leave reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get('month')
        if month and not _parse_month(month):
            return Response(
                {'error': 'Invalid month. Use YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            leaves = _scoped_leave_queryset(request, month)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid employee_id.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'month': month or 'all',
            'total_applications': leaves.count(),
            'approved_requests': leaves.filter(status='APPROVED').count(),
            'pending_requests': leaves.filter(status='PENDING').count(),
            'rejected_requests': leaves.filter(status='REJECTED').count(),
        }, status=status.HTTP_200_OK)


class LeaveReportView(APIView):
    """
    GET /hrms/leaves/report/?month=YYYY-MM[&employee_id=ID]
    Leave applications audit report:
    leave_id, staff_member, leave_type, dates, days, reason, status.
    Employees only see their own records; admins/HR see all employees.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access leave reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get('month')
        if month and not _parse_month(month):
            return Response(
                {'error': 'Invalid month. Use YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            leaves = _scoped_leave_queryset(request, month).order_by('-start_date')
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid employee_id.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report = []
        for leave in leaves:
            report.append({
                'leave_id': leave.id,
                'employee_id': leave.employee_id,
                'staff_member': leave.employee.get_full_name() or leave.employee.username,
                'leave_type': leave.leave_type,
                'leave_type_display': leave.get_leave_type_display(),
                'dates': '{} to {}'.format(leave.start_date, leave.end_date),
                'start_date': str(leave.start_date),
                'end_date': str(leave.end_date),
                'days': leave.days_count,
                'reason': leave.reason,
                'status': leave.status,
                'status_display': leave.get_status_display(),
            })

        return Response({'month': month or 'all', 'leaves': report}, status=status.HTTP_200_OK)


def _roster_employees(request):
    employees = User.objects.all()
    if not (request.user.is_superuser or request.user.role in ('admin', 'hr')):
        employees = employees.filter(pk=request.user.pk)
    return employees.exclude(role='customer').order_by('id')


def _kyc_ok(user):
    return bool(user.phone and user.date_of_birth)


def _latest_basic_salary(user):
    record = Payroll.objects.filter(employee=user).order_by('-payroll_month', '-id').first()
    return record.basic_pay if record else None


class EmployeeSummaryView(APIView):
    """
    GET /hrms/employees/summary/
    Summary: total employees, KYC compliance, average compensation, system admins.
    Employees see their own figures only; admins/HR see all employees.
    KYC compliance = % of employees with phone + date of birth on record.
    Average compensation = average latest basic salary per employee.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access employee reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        employees = list(_roster_employees(request))
        total = len(employees)
        kyc_count = sum(1 for emp in employees if _kyc_ok(emp))
        salaries = []
        for emp in employees:
            basic = _latest_basic_salary(emp)
            if basic is not None:
                salaries.append(float(basic))
        system_admins = User.objects.filter(role='admin').count()

        return Response({
            'total_employees': total,
            'kyc_compliance': round(kyc_count / total * 100, 1) if total else 0.0,
            'average_compensation': round(sum(salaries) / len(salaries), 2) if salaries else 0.0,
            'system_admins': system_admins,
        }, status=status.HTTP_200_OK)


class EmployeeDirectoryView(APIView):
    """
    GET /hrms/employees/report/
    Employee master directory & payroll scale:
    employee_id, staff_member, role, mobile, basic_salary, status(active/inactive).
    Employees see only their own row; admins/HR see all employees (optionally filtered by employee_id).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access employee reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        employees = _roster_employees(request)

        if request.user.is_superuser or request.user.role in ('admin', 'hr'):
            employee_id = request.query_params.get('employee_id')
            if employee_id:
                try:
                    employees = employees.filter(pk=int(employee_id))
                except (TypeError, ValueError):
                    return Response(
                        {'error': 'Invalid employee_id.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        directory = []
        for employee in employees:
            basic = _latest_basic_salary(employee)
            directory.append({
                'employee_id': employee.id,
                'staff_member': employee.get_full_name() or employee.username,
                'role': employee.role,
                'role_display': employee.get_role_display(),
                'mobile': employee.phone or '',
                'basic_salary': float(basic) if basic is not None else 0.0,
                'status': 'active' if employee.is_active else 'inactive',
            })

        return Response({'employees': directory}, status=status.HTTP_200_OK)


class LateComingSummaryView(APIView):
    """
    GET /hrms/late-coming/summary/?month=YYYY-MM
    Summary: late punch incidents, shift timing, center compliances (punctuality %).
    Employees see their own figures; admins/HR see all employees.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access attendance reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get('month') or timezone.localdate().strftime('%Y-%m')
        first_day = _parse_month(month)
        if not first_day:
            return Response(
                {'error': 'Invalid month. Use YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        last_day = _month_last_day(first_day)

        employees = _visible_employees(request)
        punches = AttendanceRecord.objects.filter(
            employee__in=employees, date__range=(first_day, last_day),
        ).select_related('employee')

        total = late = 0
        for record in punches:
            punch = _parse_punch(record.in_time)
            if punch is None:
                continue
            total += 1
            if _time_minutes(punch) > SHIFT_START_MINUTE:
                late += 1

        on_time = total - late
        return Response({
            'month': month,
            'shift_timing': '{} to {}'.format(SHIFT_START, SHIFT_END),
            'total_punches': total,
            'late_punch_incidents': late,
            'on_time_punches': on_time,
            'center_compliances': {
                'compliance_rate': round(on_time / total * 100, 1) if total else 0.0,
                'on_time_punches': on_time,
                'late_punches': late,
            },
        }, status=status.HTTP_200_OK)


class LateComingReportView(APIView):
    """
    GET /hrms/late-coming/report/?month=YYYY-MM[&employee_id=ID]
    Per-employee late coming detail with all punch times:
    employee_id, staff_member, role, total_punches, late_punches and each day's date,
    in_time, out_time, work_hours, late_minutes, is_late.
    Employees see their own data; admins/HR see all employees.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'customer':
            return Response(
                {'error': 'Only employees can access attendance reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get('month') or timezone.localdate().strftime('%Y-%m')
        first_day = _parse_month(month)
        if not first_day:
            return Response(
                {'error': 'Invalid month. Use YYYY-MM format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        last_day = _month_last_day(first_day)

        employees = _visible_employees(request)
        if request.user.is_superuser or request.user.role in ('admin', 'hr'):
            employee_id = request.query_params.get('employee_id')
            if employee_id:
                try:
                    employees = employees.filter(pk=int(employee_id))
                except (TypeError, ValueError):
                    return Response(
                        {'error': 'Invalid employee_id.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        report = []
        for employee in employees:
            records = AttendanceRecord.objects.filter(
                employee=employee, date__range=(first_day, last_day),
            ).order_by('date')
            punches = []
            late_count = 0
            for record in records:
                punch = _parse_punch(record.in_time)
                entry = {
                    'date': str(record.date),
                    'day_name': record.day_name,
                    'in_time': record.in_time or '',
                    'out_time': record.out_time or '',
                    'work_hours': record.work_hours,
                    'status': record.status,
                }
                if punch is not None:
                    minutes = _time_minutes(punch)
                    entry['is_late'] = minutes > SHIFT_START_MINUTE
                    entry['late_minutes'] = max(minutes - SHIFT_START_MINUTE, 0) if entry['is_late'] else 0
                    if entry['is_late']:
                        late_count += 1
                else:
                    entry['is_late'] = False
                    entry['late_minutes'] = None
                punches.append(entry)

            if punches:
                report.append({
                    'employee_id': employee.id,
                    'staff_member': employee.get_full_name() or employee.username,
                    'role': employee.role,
                    'total_punches': len(punches),
                    'late_punches': late_count,
                    'punches': punches,
                })

        return Response({
            'month': month,
            'shift_timing': '{} to {}'.format(SHIFT_START, SHIFT_END),
            'report': report,
        }, status=status.HTTP_200_OK)


# ============================================================================
# HR SETTINGS VIEWS (Company, Attendance, Leave, Notification, Roles/Permissions)
# ============================================================================

class HRSettingsView(APIView):
    """
    Combined HR Settings endpoint:
    GET: Returns Company, Attendance, Leave, Notification settings, and Roles Permissions.
    PATCH / PUT: Bulk or partial update for any or all sections.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        company = HRCompanySetting.load()
        attendance = HRAttendanceSetting.load()
        leave = HRLeaveSetting.load()
        notifications = HRNotificationSetting.load()
        
        # Ensure default roles exist
        HRRolePermission.seed_defaults()
        roles = HRRolePermission.objects.all().order_by('id')

        return Response({
            'success': True,
            'company': HRCompanySettingSerializer(company).data,
            'attendance': HRAttendanceSettingSerializer(attendance).data,
            'leave': HRLeaveSettingSerializer(leave).data,
            'notifications': HRNotificationSettingSerializer(notifications).data,
            'roles': HRRolePermissionSerializer(roles, many=True).data,
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        data = request.data
        updated_sections = []

        # 1. Company Settings
        if any(k in data for k in ['company', 'organization_name', 'opening_time', 'closing_time', 'contact_email', 'contact_phone', 'address']):
            company_data = data.get('company') if ('company' in data and isinstance(data['company'], dict)) else data
            company = HRCompanySetting.load()
            c_ser = HRCompanySettingSerializer(company, data=company_data, partial=True)
            if c_ser.is_valid():
                c_ser.save()
                updated_sections.append('company')

        # 2. Attendance Settings
        if any(k in data for k in ['attendance', 'grace_period_minutes', 'grace_period_label', 'half_day_cutoff_time', 'shift_start_time', 'shift_end_time', 'standard_work_hours']):
            att_data = data.get('attendance') if ('attendance' in data and isinstance(data['attendance'], dict)) else data
            attendance = HRAttendanceSetting.load()
            a_ser = HRAttendanceSettingSerializer(attendance, data=att_data, partial=True)
            if a_ser.is_valid():
                a_ser.save()
                updated_sections.append('attendance')

        # 3. Leave Settings
        if any(k in data for k in ['leave', 'annual_casual_leave', 'annual_sick_leave', 'annual_paid_leave']):
            leave_data = data.get('leave') if ('leave' in data and isinstance(data['leave'], dict)) else data
            leave = HRLeaveSetting.load()
            l_ser = HRLeaveSettingSerializer(leave, data=leave_data, partial=True)
            if l_ser.is_valid():
                l_ser.save()
                updated_sections.append('leave')

        # 4. Notification Settings
        if any(k in data for k in ['notifications', 'whatsapp_daily_punch_summary', 'sms_leave_approval', 'email_leave_notifications', 'admin_whatsapp_number']):
            notif_data = data.get('notifications') if ('notifications' in data and isinstance(data['notifications'], dict)) else data
            notifications = HRNotificationSetting.load()
            n_ser = HRNotificationSettingSerializer(notifications, data=notif_data, partial=True)
            if n_ser.is_valid():
                n_ser.save()
                updated_sections.append('notifications')

        # 5. Roles & Permissions (can be passed as a list of roles with id or role key)
        if 'roles' in data and isinstance(data['roles'], list):
            for r_data in data['roles']:
                role_id = r_data.get('id')
                role_key = r_data.get('role')
                role_obj = None
                if role_id:
                    role_obj = HRRolePermission.objects.filter(id=role_id).first()
                elif role_key:
                    role_obj = HRRolePermission.objects.filter(role=role_key).first()
                if role_obj:
                    r_ser = HRRolePermissionSerializer(role_obj, data=r_data, partial=True)
                    if r_ser.is_valid():
                        r_ser.save()
            updated_sections.append('roles')

        # Re-fetch everything and return
        company = HRCompanySetting.load()
        attendance = HRAttendanceSetting.load()
        leave = HRLeaveSetting.load()
        notifications = HRNotificationSetting.load()
        roles = HRRolePermission.objects.all().order_by('id')

        return Response({
            'success': True,
            'message': 'HR Settings updated successfully!',
            'updated_sections': updated_sections,
            'company': HRCompanySettingSerializer(company).data,
            'attendance': HRAttendanceSettingSerializer(attendance).data,
            'leave': HRLeaveSettingSerializer(leave).data,
            'notifications': HRNotificationSettingSerializer(notifications).data,
            'roles': HRRolePermissionSerializer(roles, many=True).data,
        }, status=status.HTTP_200_OK)

    def put(self, request):
        return self.patch(request)


class HRCompanySettingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        company = HRCompanySetting.load()
        return Response(HRCompanySettingSerializer(company).data, status=status.HTTP_200_OK)

    def patch(self, request):
        company = HRCompanySetting.load()
        serializer = HRCompanySettingSerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Company settings updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class HRAttendanceSettingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        attendance = HRAttendanceSetting.load()
        return Response(HRAttendanceSettingSerializer(attendance).data, status=status.HTTP_200_OK)

    def patch(self, request):
        attendance = HRAttendanceSetting.load()
        serializer = HRAttendanceSettingSerializer(attendance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Attendance settings updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class HRLeaveSettingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        leave = HRLeaveSetting.load()
        return Response(HRLeaveSettingSerializer(leave).data, status=status.HTTP_200_OK)

    def patch(self, request):
        leave = HRLeaveSetting.load()
        serializer = HRLeaveSettingSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Leave settings updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class HRNotificationSettingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        notifications = HRNotificationSetting.load()
        return Response(HRNotificationSettingSerializer(notifications).data, status=status.HTTP_200_OK)

    def patch(self, request):
        notifications = HRNotificationSetting.load()
        serializer = HRNotificationSettingSerializer(notifications, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Notification settings updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class HRRolePermissionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        HRRolePermission.seed_defaults()
        roles = HRRolePermission.objects.all().order_by('id')
        return Response(HRRolePermissionSerializer(roles, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HRRolePermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Role created', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HRRolePermissionDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(HRRolePermission, pk=pk)

    def get(self, request, pk):
        role = self.get_object(pk)
        return Response(HRRolePermissionSerializer(role).data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        role = self.get_object(pk)
        serializer = HRRolePermissionSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Role permissions updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        role = self.get_object(pk)
        role.delete()
        return Response({'success': True, 'message': 'Role permission removed'}, status=status.HTTP_200_OK)


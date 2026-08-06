import math
from datetime import date, datetime
from calendar import monthrange

from django.db.models import Sum, Count, Avg, Q, F, DecimalField, Value
from django.db.models.functions import Coalesce


def calculate_distance(lat1, lng1, lat2, lng2):
    """Haversine formula to calculate distance between two GPS coordinates in km."""
    if not all([lat1, lng1, lat2, lng2]):
        return 0.0

    lat1 = float(lat1)
    lng1 = float(lng1)
    lat2 = float(lat2)
    lng2 = float(lng2)

    R = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (math.sin(delta_lat / 2) ** 2
         + math.cos(lat1_rad) * math.cos(lat2_rad)
         * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)


def get_date_range(year, month):
    """Return (start_date, end_date) for the given year/month."""
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    return start_date, end_date


def aggregate_employee_sales(employee_id, start_date, end_date):
    """Return total sales revenue for an employee within a date range."""
    try:
        from apps.sales.models import SalesOrder
        result = SalesOrder.objects.filter(
            employee_id=employee_id,
            date__gte=start_date,
            date__lte=end_date,
            status__in=['in_progress', 'completed'],
        ).aggregate(total=Coalesce(
            Sum('total_amount'),
            Value(0, output_field=DecimalField()),
        ))
        return result['total']
    except (ImportError, LookupError):
        return 0


def aggregate_employee_visits(employee_id, start_date, end_date):
    """Return total visits for an employee within a date range."""
    try:
        from apps.visits.models import Visit
        return Visit.objects.filter(
            employee_id=employee_id,
            check_in_time__date__gte=start_date,
            check_in_time__date__lte=end_date,
        ).count()
    except (ImportError, LookupError):
        return 0


def aggregate_employee_attendance(employee_id, start_date, end_date):
    """Return attendance stats for an employee within a date range."""
    try:
        from apps.attendance.models import Attendance
        total_days = Attendance.objects.filter(
            employee_id=employee_id,
            date__gte=start_date,
            date__lte=end_date,
        ).count()
        present_days = Attendance.objects.filter(
            employee_id=employee_id,
            date__gte=start_date,
            date__lte=end_date,
            status='present',
        ).count()
        total_calendar_days = (end_date - start_date).days + 1
        attendance_pct = 0.0
        if total_calendar_days > 0:
            attendance_pct = round((present_days / total_calendar_days) * 100, 2)
        return {
            'total_days': total_days,
            'present_days': present_days,
            'attendance_percentage': attendance_pct,
        }
    except (ImportError, LookupError):
        return {
            'total_days': 0,
            'present_days': 0,
            'attendance_percentage': 0.0,
        }


def aggregate_employee_distance(employee_id, start_date, end_date):
    """Return total distance traveled by an employee within a date range."""
    try:
        from apps.tracking.models import TrackingLocation
        count = TrackingLocation.objects.filter(
            employee_id=employee_id,
            timestamp__gte=start_date,
            timestamp__lte=end_date,
        ).count()
        return count * 0.5
    except (ImportError, LookupError):
        return 0


def aggregate_employee_targets(employee_id, start_date, end_date):
    """Return total target amount and achievement percentage for an employee."""
    try:
        from apps.targets.models import Target
        target_result = Target.objects.filter(
            employee_id=employee_id,
            month=start_date.month,
            year=start_date.year,
        ).aggregate(total=Coalesce(
            Sum('target_amount'),
            Value(0, output_field=DecimalField()),
        ))
        total_target = target_result['total']
        achieved = aggregate_employee_sales(employee_id, start_date, end_date)
        achievement_pct = 0.0
        if total_target > 0:
            achievement_pct = round(float(achieved / total_target) * 100, 2)
        return {
            'total_target': total_target,
            'achieved': achieved,
            'achievement_percentage': achievement_pct,
        }
    except (ImportError, LookupError):
        return {
            'total_target': 0,
            'achieved': 0,
            'achievement_percentage': 0.0,
        }

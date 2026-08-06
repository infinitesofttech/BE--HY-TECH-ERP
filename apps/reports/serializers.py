from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    today_attendance = serializers.IntegerField()
    online_employees = serializers.IntegerField()
    total_dealers = serializers.IntegerField()
    total_retailers = serializers.IntegerField()
    total_sales_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_leaves = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class EmployeePerformanceSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    email = serializers.EmailField()
    territory = serializers.CharField(allow_blank=True)
    pin_code = serializers.CharField(allow_blank=True)
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_visits = serializers.IntegerField()
    attendance_days = serializers.IntegerField()
    total_calendar_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
    total_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_target = serializers.DecimalField(max_digits=12, decimal_places=2)
    target_achievement_percentage = serializers.FloatField()


class CompareEmployeeSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_visits = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
    total_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_target = serializers.DecimalField(max_digits=12, decimal_places=2)
    target_achievement_percentage = serializers.FloatField()


class CompareSerializer(serializers.Serializer):
    employee_a = CompareEmployeeSerializer()
    employee_b = CompareEmployeeSerializer()


class WeakAreaSerializer(serializers.Serializer):
    territory = serializers.CharField()
    pin_code = serializers.CharField(allow_blank=True, allow_null=True)
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_visits = serializers.IntegerField()
    employee_count = serializers.IntegerField()
    avg_sales_per_employee = serializers.DecimalField(max_digits=12, decimal_places=2)
    weak_dealers_count = serializers.IntegerField()
    target_missed = serializers.BooleanField()
    recommendations = serializers.ListField(child=serializers.CharField())


class LeadReportSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    lead_name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, allow_null=True)
    phone = serializers.CharField(allow_blank=True, allow_null=True)
    lead_status = serializers.CharField()
    created_date = serializers.DateField()
    lead_owner = serializers.CharField(allow_blank=True, allow_null=True)


class DealReportSerializer(serializers.Serializer):
    deal_id = serializers.IntegerField()
    deal_name = serializers.CharField()
    stage = serializers.CharField(allow_null=True, required=False)
    progress = serializers.CharField(allow_null=True, required=False)
    deal_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    tags = serializers.CharField(allow_blank=True, allow_null=True)
    expected_close_date = serializers.DateField(allow_null=True)
    probability = serializers.IntegerField()
    status = serializers.CharField()


class ContactReportSerializer(serializers.Serializer):
    contact_id = serializers.IntegerField()
    name = serializers.CharField()
    phone = serializers.CharField(allow_blank=True, allow_null=True)
    tags = serializers.CharField(allow_blank=True, allow_null=True)
    location = serializers.CharField(allow_blank=True, allow_null=True)
    rating = serializers.CharField(allow_blank=True, allow_null=True)
    contact = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField()


class CompanyReportSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField(allow_blank=True, allow_null=True)
    tags = serializers.CharField(allow_blank=True, allow_null=True)
    owner = serializers.CharField(allow_blank=True, allow_null=True)
    contact = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField()


class RevenueReportSerializer(serializers.Serializer):
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    new_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    expansion_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    mrr = serializers.DecimalField(max_digits=14, decimal_places=2)
    arr = serializers.DecimalField(max_digits=14, decimal_places=2)
    growth = serializers.FloatField(allow_null=True)
    churn_impact = serializers.FloatField()


class ProjectReportSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    name = serializers.CharField()
    client = serializers.CharField(allow_blank=True, allow_null=True)
    priority = serializers.CharField()
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    pipeline_stage = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField()


class TaskReportSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    title = serializers.CharField()
    category = serializers.CharField()
    status = serializers.CharField()
    priority = serializers.CharField()
    tags = serializers.CharField(allow_blank=True, allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    assignees = serializers.ListField(child=serializers.CharField())


class AttendanceReportSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    period = serializers.CharField()
    total_working_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_entries = serializers.IntegerField()
    average_work_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    attendance_rate = serializers.FloatField()


class LeaveReportSerializer(serializers.Serializer):
    leave_type = serializers.CharField()
    allocated = serializers.IntegerField()
    remaining = serializers.IntegerField()
    used = serializers.IntegerField()
    pending = serializers.IntegerField()
    utilization = serializers.FloatField()

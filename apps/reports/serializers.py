from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    today_attendance = serializers.IntegerField()
    online_employees = serializers.IntegerField()
    total_dealers = serializers.IntegerField()
    total_retailers = serializers.IntegerField()
    total_mechanics = serializers.IntegerField()
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

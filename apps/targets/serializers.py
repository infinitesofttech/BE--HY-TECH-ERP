from rest_framework import serializers
from django.db.models import Sum
from .models import Target


class TargetSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)

    class Meta:
        model = Target
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'month', 'year', 'target_amount', 'achieved_amount',
            'status', 'product', 'product_name',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TargetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = [
            'id', 'employee', 'month', 'year', 'target_amount',
            'achieved_amount', 'status', 'product', 'notes',
        ]
        read_only_fields = ['id']

    def validate_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError('Month must be between 1 and 12.')
        return value

    def validate_year(self, value):
        if value < 2020 or value > 2100:
            raise serializers.ValidationError('Year must be a valid year.')
        return value

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Target amount must be greater than 0.')
        return value


class TargetWithAchievementSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    achieved_amount = serializers.SerializerMethodField()
    pending_amount = serializers.SerializerMethodField()
    achievement_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Target
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'month', 'year', 'target_amount', 'achieved_amount',
            'status', 'pending_amount', 'achievement_percentage',
            'product', 'product_name', 'notes',
            'created_at', 'updated_at',
        ]

    def _get_achieved(self, obj):
        from apps.sales.models import SalesReport, SalesReportItem

        query = SalesReport.objects.filter(
            employee=obj.employee,
            date__year=obj.year,
            date__month=obj.month,
        )

        if obj.product:
            total = SalesReportItem.objects.filter(
                report__in=query,
                product=obj.product,
            ).aggregate(total=Sum('total'))['total'] or 0
        else:
            total = query.aggregate(total=Sum('total_revenue'))['total'] or 0

        return float(total)

    def get_achieved_amount(self, obj):
        return self._get_achieved(obj)

    def get_pending_amount(self, obj):
        achieved = self._get_achieved(obj)
        pending = float(obj.target_amount) - achieved
        return max(pending, 0)

    def get_achievement_percentage(self, obj):
        achieved = self._get_achieved(obj)
        if obj.target_amount == 0:
            return 0
        return round((achieved / float(obj.target_amount)) * 100, 2)

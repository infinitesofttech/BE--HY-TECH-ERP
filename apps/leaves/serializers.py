from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import LeaveType, Leave, LeaveApprovalWorkflow, LeaveAllocation

User = get_user_model()


def get_allocation(employee, leave_type, year):
    return LeaveAllocation.objects.filter(
        employee=employee, leave_type=leave_type, year=year
    ).first()


class LeaveApprovalWorkflowSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    approver_email = serializers.CharField(source='approver.email', read_only=True)

    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'approver', 'approver_name', 'approver_email',
            'priority', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class LeaveAllocationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveAllocation
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'leave_type', 'leave_type_name', 'allotted_days', 'year',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_allotted_days(self, value):
        if value < 1:
            raise serializers.ValidationError('Allotted days must be at least 1.')
        return value

    def validate_year(self, value):
        from django.utils import timezone
        if value < 2020 or value > timezone.localtime().year + 1:
            raise serializers.ValidationError('Invalid year.')
        return value


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'days_allowed', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    assigned_approver_name = serializers.CharField(
        source='assigned_approver.get_full_name', read_only=True, default=None,
    )
    assigned_approver_email = serializers.CharField(
        source='assigned_approver.email', read_only=True, default=None,
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name', read_only=True, default=None,
    )

    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_name', 'employee_email',
            'leave_type', 'leave_type_name', 'start_date', 'end_date',
            'reason', 'total_days', 'status',
            'assigned_approver', 'assigned_approver_name', 'assigned_approver_email',
            'approved_by', 'approved_by_name',
            'approved_at', 'rejection_reason', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'total_days', 'status', 'assigned_approver',
            'approved_by', 'approved_at', 'rejection_reason', 'created_at', 'updated_at',
        ]


class LeaveCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            'id', 'leave_type', 'start_date', 'end_date', 'reason',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError('End date must be after start date.')

        if attrs['start_date'] < timezone.now().date():
            raise serializers.ValidationError('Cannot request leave for past dates.')

        employee = self.context['request'].user
        leave_type = attrs['leave_type']
        year = attrs['start_date'].year

        allocation = get_allocation(employee, leave_type, year)
        if not allocation:
            raise serializers.ValidationError(
                f'Leave "{leave_type.name}" is not allocated to you.'
            )

        used_days = Leave.objects.filter(
            employee=employee,
            leave_type=leave_type,
            status='approved',
            start_date__year=year,
        ).aggregate(total=serializers.models.Sum('total_days'))['total'] or 0

        requested_days = (attrs['end_date'] - attrs['start_date']).days + 1

        if used_days + requested_days > allocation.allotted_days:
            remaining = allocation.allotted_days - used_days
            raise serializers.ValidationError(
                f'Insufficient leave balance. Remaining: {remaining} days, Requested: {requested_days} days.'
            )

        return attrs

    def create(self, validated_data):
        employee = self.context['request'].user
        validated_data['employee'] = employee

        workflow = LeaveApprovalWorkflow.objects.filter(
            employee=employee, is_active=True
        ).order_by('priority').first()

        if workflow:
            validated_data['assigned_approver'] = workflow.approver
        else:
            admin = User.objects.filter(role='super_admin', is_active=True).first()
            validated_data['assigned_approver'] = admin

        return super().create(validated_data)


class LeaveApproveSerializer(serializers.Serializer):
    pass


class LeaveRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default='')


class LeaveAdminAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'leave_type', 'start_date', 'end_date', 'reason',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError('End date must be after start date.')

        employee = attrs['employee']
        leave_type = attrs['leave_type']
        year = attrs['start_date'].year

        allocation = get_allocation(employee, leave_type, year)
        if not allocation:
            raise serializers.ValidationError(
                f'Leave "{leave_type.name}" is not allocated to this employee.'
            )

        used_days = Leave.objects.filter(
            employee=employee,
            leave_type=leave_type,
            status='approved',
            start_date__year=year,
        ).aggregate(total=serializers.models.Sum('total_days'))['total'] or 0

        requested_days = (attrs['end_date'] - attrs['start_date']).days + 1

        if used_days + requested_days > allocation.allotted_days:
            remaining = allocation.allotted_days - used_days
            raise serializers.ValidationError(
                f'Insufficient leave balance. Remaining: {remaining} days, Requested: {requested_days} days.'
            )

        return attrs

    def create(self, validated_data):
        employee = validated_data['employee']

        workflow = LeaveApprovalWorkflow.objects.filter(
            employee=employee, is_active=True
        ).order_by('priority').first()

        if workflow:
            validated_data['assigned_approver'] = workflow.approver
        else:
            admin = User.objects.filter(role='super_admin', is_active=True).first()
            validated_data['assigned_approver'] = admin

        return super().create(validated_data)

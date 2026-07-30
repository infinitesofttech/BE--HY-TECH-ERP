from django.utils import timezone
from django.db import models
from django.db.models import Sum

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsManagerOrAbove
from .models import LeaveType, Leave, LeaveApprovalWorkflow, LeaveAllocation
from .serializers import (
    LeaveTypeSerializer,
    LeaveSerializer,
    LeaveCreateSerializer,
    LeaveApproveSerializer,
    LeaveRejectSerializer,
    LeaveApprovalWorkflowSerializer,
    LeaveAdminAssignSerializer,
    LeaveAllocationSerializer,
)


class LeaveApprovalWorkflowListCreateView(generics.ListCreateAPIView):
    queryset = LeaveApprovalWorkflow.objects.select_related('employee', 'approver').all()
    serializer_class = LeaveApprovalWorkflowSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get_queryset(self):
        qs = self.queryset
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs


class LeaveApprovalWorkflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveApprovalWorkflow.objects.select_related('employee', 'approver').all()
    serializer_class = LeaveApprovalWorkflowSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class LeaveTypeListCreateView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class LeaveTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class LeaveCreateView(generics.CreateAPIView):
    serializer_class = LeaveCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = LeaveSerializer(serializer.instance, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class LeaveListView(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Leave.objects.select_related(
            'employee', 'leave_type', 'approved_by', 'assigned_approver'
        ).all()

        if user.role == 'super_admin':
            pass
        elif user.role == 'manager':
            qs = qs.filter(
                models.Q(employee=user) | models.Q(assigned_approver=user)
            )
        else:
            qs = qs.filter(employee=user)

        status_filter = self.request.query_params.get('status')
        employee_filter = self.request.query_params.get('employee')
        leave_type_filter = self.request.query_params.get('leave_type')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if status_filter:
            qs = qs.filter(status=status_filter)
        if employee_filter:
            qs = qs.filter(employee_id=employee_filter)
        if leave_type_filter:
            qs = qs.filter(leave_type_id=leave_type_filter)
        if month:
            qs = qs.filter(start_date__month=month)
        if year:
            qs = qs.filter(start_date__year=year)

        return qs


class MyLeaveListView(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Leave.objects.filter(
            employee=self.request.user
        ).select_related('employee', 'leave_type', 'approved_by', 'assigned_approver')


class PendingApprovalsView(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Leave.objects.filter(
            assigned_approver=user, status='pending'
        ).select_related('employee', 'leave_type', 'approved_by', 'assigned_approver')

        if user.role == 'super_admin':
            qs = Leave.objects.filter(
                status='pending'
            ).select_related('employee', 'leave_type', 'approved_by', 'assigned_approver')

        return qs


class LeaveDetailView(generics.RetrieveAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Leave.objects.select_related(
                'employee', 'leave_type', 'approved_by', 'assigned_approver'
            ).all()
        return Leave.objects.filter(
            models.Q(employee=user) | models.Q(assigned_approver=user)
        ).select_related('employee', 'leave_type', 'approved_by', 'assigned_approver')


class LeaveApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            leave = Leave.objects.get(pk=pk)
        except Leave.DoesNotExist:
            return Response(
                {'error': 'Leave not found.'}, status=status.HTTP_404_NOT_FOUND,
            )

        if leave.status != 'pending':
            return Response(
                {'error': f'Cannot approve a leave with status "{leave.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role != 'super_admin' and leave.assigned_approver != request.user:
            return Response(
                {'error': 'You are not authorized to approve this leave.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.save()

        serializer = LeaveSerializer(leave, context={'request': request})
        return Response(serializer.data)


class LeaveRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            leave = Leave.objects.get(pk=pk)
        except Leave.DoesNotExist:
            return Response(
                {'error': 'Leave not found.'}, status=status.HTTP_404_NOT_FOUND,
            )

        if leave.status != 'pending':
            return Response(
                {'error': f'Cannot reject a leave with status "{leave.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role != 'super_admin' and leave.assigned_approver != request.user:
            return Response(
                {'error': 'You are not authorized to reject this leave.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LeaveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        leave.status = 'rejected'
        leave.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.save()

        output = LeaveSerializer(leave, context={'request': request})
        return Response(output.data)


class LeaveBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id):
        if request.user.role not in ('super_admin', 'manager'):
            if request.user.pk != employee_id:
                return Response(
                    {'error': 'You can only view your own leave balance.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        current_year = timezone.localtime().year
        allocations = LeaveAllocation.objects.filter(
            employee_id=employee_id, year=current_year
        )

        balances = []
        for al in allocations:
            used_days = Leave.objects.filter(
                employee_id=employee_id,
                leave_type=al.leave_type,
                status='approved',
                start_date__year=current_year,
            ).aggregate(total=Sum('total_days'))['total'] or 0

            remaining = al.allotted_days - used_days

            balances.append({
                'leave_type': al.leave_type.id,
                'leave_type_name': al.leave_type.name,
                'total_allowed': al.allotted_days,
                'used_days': used_days,
                'remaining_days': remaining,
            })

        return Response({
            'employee_id': employee_id,
            'year': current_year,
            'balances': balances,
        })


class LeaveAdminAssignView(generics.CreateAPIView):
    serializer_class = LeaveAdminAssignSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = LeaveSerializer(serializer.instance, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class LeaveAllocationListCreateView(generics.ListCreateAPIView):
    queryset = LeaveAllocation.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveAllocationSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get_queryset(self):
        qs = self.queryset
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)
        return qs


class LeaveAllocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveAllocation.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveAllocationSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

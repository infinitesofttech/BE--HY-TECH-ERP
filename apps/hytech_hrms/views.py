from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import AttendanceRecord, LeaveRecord, LeaveBalance, HolidayItem
from .serializers import (
    AttendanceRecordSerializer, LeaveRecordSerializer,
    LeaveBalanceSerializer, HolidayItemSerializer
)

User = get_user_model()


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

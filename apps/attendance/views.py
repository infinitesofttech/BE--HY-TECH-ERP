from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import AttendanceType, Attendance
from .serializers import (
    AttendanceTypeSerializer, AttendanceSerializer, AttendancePunchInSerializer,
    AttendancePunchOutSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


class AttendanceTypeListCreateView(generics.ListCreateAPIView):
    queryset = AttendanceType.objects.filter(is_active=True)
    serializer_class = AttendanceTypeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class AttendanceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendanceType.objects.all()
    serializer_class = AttendanceTypeSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]


class AttendancePunchInView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AttendancePunchInSerializer, responses={200: AttendanceSerializer})
    def post(self, request):
        serializer = AttendancePunchInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        today = timezone.localtime().date()
        attendance, created = Attendance.objects.get_or_create(
            employee=request.user, date=today
        )

        if attendance.punch_in_time and not attendance.punch_out_time:
            return Response(
                {'error': 'Already punched in today. Please punch out first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.punch_out_time:
            return Response(
                {'error': 'Already punched in and out today.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.punch_in_time = timezone.localtime()
        attendance.punch_in_lat = serializer.validated_data['latitude']
        attendance.punch_in_lng = serializer.validated_data['longitude']
        attendance.punch_in_address = serializer.validated_data.get('address', '')
        attendance.status = 'present'
        attendance.save()

        return Response(
            AttendanceSerializer(attendance).data,
            status=status.HTTP_200_OK
        )


class AttendancePunchOutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AttendancePunchOutSerializer, responses={200: AttendanceSerializer})
    def post(self, request):
        serializer = AttendancePunchOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        today = timezone.localtime().date()
        try:
            attendance = Attendance.objects.get(employee=request.user, date=today)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'No punch-in found for today.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.punch_out_time:
            return Response(
                {'error': 'Already punched out today.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not attendance.punch_in_time:
            return Response(
                {'error': 'You must punch in before punching out.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.punch_out_time = timezone.localtime()
        attendance.punch_out_lat = serializer.validated_data['latitude']
        attendance.punch_out_lng = serializer.validated_data['longitude']
        attendance.punch_out_address = serializer.validated_data.get('address', '')
        attendance.save()

        return Response(
            AttendanceSerializer(attendance).data,
            status=status.HTTP_200_OK
        )


class TodayAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localtime().date()
        employee_id = request.query_params.get('employee_id')

        if employee_id:
            if request.user.role not in ['super_admin', 'manager']:
                return Response({'error': 'Not allowed to view others attendance.'}, status=status.HTTP_403_FORBIDDEN)
            try:
                attendance = Attendance.objects.get(employee_id=employee_id, date=today)
                return Response(AttendanceSerializer(attendance).data)
            except Attendance.DoesNotExist:
                return Response({'message': 'No attendance record for today.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role in ['super_admin', 'manager']:
            attendances = Attendance.objects.filter(date=today)
            return Response(AttendanceSerializer(attendances, many=True).data)

        try:
            attendance = Attendance.objects.get(employee=request.user, date=today)
            return Response(AttendanceSerializer(attendance).data)
        except Attendance.DoesNotExist:
            return Response({'message': 'No attendance record for today.'}, status=status.HTTP_404_NOT_FOUND)


class AttendanceHistoryView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'employee']
    search_fields = ['employee__email', 'employee__first_name']
    ordering_fields = ['date']
    pagination_class = None

    def get_queryset(self):
        qs = Attendance.objects.all()
        user = self.request.user
        if user.role == 'msr':
            qs = qs.filter(employee=user)

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs


class AttendanceDailyReportView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        date_str = request.query_params.get('date', timezone.localtime().date().isoformat())
        from datetime import date as dt
        try:
            report_date = dt.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                          status=status.HTTP_400_BAD_REQUEST)

        attendances = Attendance.objects.filter(date=report_date)
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)


class AttendanceMonthlyReportView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        month = request.query_params.get('month', timezone.localtime().month)
        year = request.query_params.get('year', timezone.localtime().year)

        from django.contrib.auth import get_user_model
        from django.db.models import Count, Sum, Q, Avg

        User = get_user_model()
        employees = User.objects.filter(is_active=True, role='msr')

        report = []
        for emp in employees:
            attendances = Attendance.objects.filter(
                employee=emp, date__month=month, date__year=year
            )
            stats = attendances.aggregate(
                total_present=Count('id', filter=Q(status='present')),
                total_absent=Count('id', filter=Q(status='absent')),
                total_late=Count('id', filter=Q(status='late')),
                total_hours=Sum('total_hours'),
                total_overtime=Sum('overtime'),
            )
            report.append({
                'employee_id': emp.id,
                'employee_email': emp.email,
                'total_present': stats['total_present'] or 0,
                'total_absent': stats['total_absent'] or 0,
                'total_late': stats['total_late'] or 0,
                'total_hours': float(stats['total_hours'] or 0),
                'total_overtime': float(stats['total_overtime'] or 0),
            })

        return Response(report)


class AttendanceExportView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get(self, request):
        from openpyxl import Workbook

        month = request.query_params.get('month', timezone.localtime().month)
        year = request.query_params.get('year', timezone.localtime().year)

        attendances = Attendance.objects.filter(
            date__month=month, date__year=year
        ).select_related('employee')

        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance Report"
        ws.append(['Employee', 'Date', 'Status', 'Punch In', 'Punch Out', 'Total Hours', 'Overtime'])

        for att in attendances:
            ws.append([
                att.employee.email,
                str(att.date),
                att.status,
                str(att.punch_in_time) if att.punch_in_time else '',
                str(att.punch_out_time) if att.punch_out_time else '',
                float(att.total_hours),
                float(att.overtime),
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=attendance_report_{month}_{year}.xlsx'
        wb.save(response)
        return response

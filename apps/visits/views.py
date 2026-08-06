from datetime import datetime

from django.db.models import Count, Avg, Q
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

import openpyxl

from apps.accounts.permissions import IsSuperAdmin, IsManagerOrAbove, IsMSR
from .models import Visit
from .serializers import (
    VisitSerializer,
    VisitCheckInSerializer,
    VisitCheckOutSerializer,
)


class VisitCheckInView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    @extend_schema(request=VisitCheckInSerializer, responses={201: VisitSerializer})
    def post(self, request):
        existing = Visit.objects.filter(
            employee=request.user, status='in_progress',
        ).first()
        if existing:
            return Response(
                {'detail': 'You already have an in-progress visit. Please check out first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VisitCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit = Visit.objects.create(
            employee=request.user,
            visit_type=data['visit_type'],
            dealer_id=data.get('dealer_id'),
            retailer_id=data.get('retailer_id'),
            purpose=data.get('purpose', ''),
            remarks=data.get('remarks', ''),
            photo=data.get('photo'),
            check_in_lat=data['check_in_lat'],
            check_in_lng=data['check_in_lng'],
            check_in_address=data.get('check_in_address', ''),
        )

        return Response(
            VisitSerializer(visit).data,
            status=status.HTTP_201_CREATED,
        )


class VisitCheckOutView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    @extend_schema(request=VisitCheckOutSerializer, responses={200: VisitSerializer})
    def post(self, request):
        visit = Visit.objects.filter(
            employee=request.user, status='in_progress',
        ).first()
        if not visit:
            return Response(
                {'detail': 'No in-progress visit found. Please check in first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VisitCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit.check_out_time = timezone.now()
        visit.check_out_lat = data['check_out_lat']
        visit.check_out_lng = data['check_out_lng']
        visit.check_out_address = data.get('check_out_address', '')

        if data.get('remarks'):
            visit.remarks = (
                f"{visit.remarks}\n--- Checkout Remarks ---\n{data['remarks']}"
                if visit.remarks
                else data['remarks']
            )

        visit.status = 'completed'
        visit.save()

        return Response(
            VisitSerializer(visit).data,
            status=status.HTTP_200_OK,
        )


class VisitListView(generics.ListAPIView):
    serializer_class = VisitSerializer
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['purpose', 'remarks']
    ordering_fields = ['check_in_time', 'created_at']

    def get_queryset(self):
        qs = Visit.objects.select_related(
            'employee', 'dealer', 'retailer',
        ).all()

        employee = self.request.query_params.get('employee')
        if employee:
            qs = qs.filter(employee_id=employee)

        visit_type = self.request.query_params.get('visit_type')
        if visit_type:
            qs = qs.filter(visit_type=visit_type)

        visit_status = self.request.query_params.get('status')
        if visit_status:
            qs = qs.filter(status=visit_status)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(check_in_time__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(check_in_time__date__lte=date_to)

        dealer = self.request.query_params.get('dealer')
        if dealer:
            qs = qs.filter(dealer_id=dealer)

        retailer = self.request.query_params.get('retailer')
        if retailer:
            qs = qs.filter(retailer_id=retailer)

        return qs


class VisitDetailView(generics.RetrieveAPIView):
    serializer_class = VisitSerializer
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    def get_queryset(self):
        return Visit.objects.select_related(
            'employee', 'dealer', 'retailer',
        ).all()


class TodayVisitsView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    def get(self, request):
        today = timezone.now().date()
        visits = Visit.objects.filter(
            employee=request.user,
            check_in_time__date=today,
        ).select_related('dealer', 'retailer').order_by('-check_in_time')

        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VisitReportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        qs = Visit.objects.all()

        if date_from:
            qs = qs.filter(check_in_time__date__gte=date_from)
        if date_to:
            qs = qs.filter(check_in_time__date__lte=date_to)

        aggregated = qs.aggregate(
            total_visits=Count('id'),
            avg_duration=Avg('duration'),
            dealer_count=Count('id', filter=Q(visit_type='dealer')),
            retailer_count=Count('id', filter=Q(visit_type='retailer')),
            unique_employees=Count('employee', distinct=True),
        )

        return Response({
            'total_visits': aggregated['total_visits'] or 0,
            'by_type': {
                'dealer': aggregated['dealer_count'] or 0,
                'retailer': aggregated['retailer_count'] or 0,
            },
            'avg_duration': str(aggregated['avg_duration']) if aggregated['avg_duration'] else None,
            'unique_employees_visiting': aggregated['unique_employees'] or 0,
        }, status=status.HTTP_200_OK)


class VisitExportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        qs = Visit.objects.select_related(
            'employee', 'dealer', 'retailer',
        ).all()

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(check_in_time__date__gte=date_from)
        if date_to:
            qs = qs.filter(check_in_time__date__lte=date_to)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Visits Report'

        headers = [
            'ID', 'Employee', 'Visit Type', 'Dealer', 'Retailer',
            'Purpose', 'Remarks', 'Status', 'Duration',
            'Check In Time', 'Check In Address', 'Check Out Time',
            'Check Out Address', 'Created At',
        ]
        ws.append(headers)

        for visit in qs:
            ws.append([
                visit.id,
                visit.employee.get_full_name() or visit.employee.email,
                visit.get_visit_type_display(),
                visit.dealer.name if visit.dealer else 'N/A',
                visit.retailer.name if visit.retailer else 'N/A',
                visit.purpose,
                visit.remarks,
                visit.get_status_display(),
                str(visit.duration) if visit.duration else 'N/A',
                visit.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                visit.check_in_address,
                visit.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if visit.check_out_time else 'N/A',
                visit.check_out_address,
                visit.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        for column in ws.columns:
            max_length = 0
            col_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_length + 2, 50)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f'visits_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response

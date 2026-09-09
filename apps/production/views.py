from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.drawing.image import Image
from django.conf import settings
import os

from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from . import services
from .models import (
    Bom,
    DailyWorkEntry,
    Dispatch,
    FinishedGoods,
    GoodsReceiptNote,
    JobOrder,
    Machine,
    MaterialIssueSlip,
    ProductionProcess,
    ProductionStage,
    PurchaseRequisition,
    QualityInspection,
    Worker,
)
from .serializers import (
    BomCreateSerializer,
    BomSerializer,
    DailyWorkEntryCreateSerializer,
    DailyWorkEntrySerializer,
    DispatchCreateSerializer,
    DispatchSerializer,
    FinishedGoodsSerializer,
    GoodsReceiptNoteCreateSerializer,
    GoodsReceiptNoteSerializer,
    JobOrderCreateSerializer,
    JobOrderSerializer,
    MachineSerializer,
    MaterialIssueSlipSerializer,
    ProductionProcessSerializer,
    ProductionStageSerializer,
    PurchaseRequisitionSerializer,
    QualityInspectionSerializer,
    WorkerCreateSerializer,
    WorkerSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


class MachineListCreateView(generics.ListCreateAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'machine_type']
    search_fields = ['name', 'code', 'machine_type']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class MachineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ProductionStageListCreateView(generics.ListCreateAPIView):
    queryset = ProductionStage.objects.all()
    serializer_class = ProductionStageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['sequence', 'name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class ProductionStageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionStage.objects.all()
    serializer_class = ProductionStageSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class BomListCreateView(generics.ListCreateAPIView):
    queryset = Bom.objects.prefetch_related('items__raw_material').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'status']
    search_fields = ['name', 'product__name', 'version']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BomCreateSerializer
        return BomSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class BomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bom.objects.prefetch_related('items__raw_material').all()
    serializer_class = BomSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class JobOrderListCreateView(generics.ListCreateAPIView):
    queryset = JobOrder.objects.select_related(
        'sales_order', 'customer', 'product', 'machine', 'supervisor', 'bom',
    ).prefetch_related(
        'operators', 'workers', 'material_requirements__raw_material',
        'processes', 'processes__worker__user', 'finished_goods',
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'product', 'customer', 'machine', 'sales_order']
    search_fields = ['job_no', 'product__name', 'customer__name']
    ordering_fields = ['start_date', 'created_at', 'priority', 'progress']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobOrderCreateSerializer
        return JobOrderSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_order = serializer.save()
        return Response(
            JobOrderSerializer(job_order).data,
            status=status.HTTP_201_CREATED,
        )


class JobOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobOrder.objects.select_related(
        'sales_order', 'customer', 'product', 'machine', 'supervisor', 'bom',
    ).prefetch_related(
        'operators', 'workers', 'material_requirements__raw_material',
        'processes', 'processes__worker__user', 'finished_goods',
    ).all()
    serializer_class = JobOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class JobOrderCheckStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return JobOrder.objects.get(pk=self.kwargs['pk'])

    def post(self, request, pk):
        job_order = self.get_object()
        requirements = services.check_stock(job_order)
        job_order.refresh_from_db()
        return Response({
            'job_order': JobOrderSerializer(job_order).data,
            'requirements': [
                {
                    'raw_material': r.raw_material.name,
                    'required_quantity': float(r.required_quantity),
                    'available_quantity': float(r.available_quantity),
                    'status': r.status,
                }
                for r in requirements
            ],
        }, status=status.HTTP_200_OK)


class JobOrderIssueMaterialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job_order = JobOrder.objects.get(pk=pk)
        try:
            slip = services.issue_material(
                job_order,
                issued_to=request.data.get('issued_to'),
                created_by=request.user,
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            MaterialIssueSlipSerializer(slip).data,
            status=status.HTTP_201_CREATED,
        )


class JobOrderCreateRequisitionView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def post(self, request, pk):
        job_order = JobOrder.objects.get(pk=pk)
        try:
            requisition = services.create_purchase_requisition(
                job_order,
                requested_by=request.user,
                department=request.data.get(
                    'department', 'Production',
                ),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            PurchaseRequisitionSerializer(requisition).data,
            status=status.HTTP_201_CREATED,
        )


class JobOrderStartProductionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job_order = JobOrder.objects.get(pk=pk)
        try:
            job_order = services.start_production(
                job_order,
                machine=request.data.get('machine'),
                supervisor=request.data.get('supervisor'),
                operators=request.data.get('operators'),
                process_names=request.data.get('processes'),
                workers=request.data.get('workers'),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            JobOrderSerializer(job_order).data, status=status.HTTP_200_OK,
        )


class JobOrderReworkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job_order = JobOrder.objects.get(pk=pk)
        services.rework_process(
            job_order, notes=request.data.get('notes'),
        )
        job_order.refresh_from_db()
        return Response(
            JobOrderSerializer(job_order).data, status=status.HTTP_200_OK,
        )


class JobOrderQcView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job_order = JobOrder.objects.get(pk=pk)
        passed = bool(request.data.get('passed', True))
        try:
            finished = services.record_qc_result(
                job_order,
                passed=passed,
                inspected_by=request.user,
                notes=request.data.get('notes'),
                warehouse=request.data.get('warehouse'),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        job_order.refresh_from_db()
        return Response({
            'job_order': JobOrderSerializer(job_order).data,
            'finished_goods': (
                FinishedGoodsSerializer(finished).data if finished else None
            ),
        }, status=status.HTTP_200_OK)


class JobOrderDispatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job_order = JobOrder.objects.get(pk=pk)
        try:
            dispatch = services.create_dispatch(
                job_order,
                packing_note=request.data.get('packing_note', ''),
                transport_mode=request.data.get('transport_mode', ''),
                vehicle_number=request.data.get('vehicle_number', ''),
                driver_name=request.data.get('driver_name', ''),
                driver_phone=request.data.get('driver_phone', ''),
                label_printed=request.data.get('label_printed', True),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            DispatchSerializer(dispatch).data, status=status.HTTP_201_CREATED,
        )


class MaterialIssueSlipListView(generics.ListAPIView):
    serializer_class = MaterialIssueSlipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_order', 'status']
    search_fields = ['slip_no', 'job_order__job_no']
    ordering_fields = ['issue_date', 'created_at']

    def get_queryset(self):
        return MaterialIssueSlip.objects.select_related(
            'job_order', 'issued_to', 'created_by', 'issued_to_worker__user',
        ).prefetch_related('items__raw_material', 'items__warehouse').all()


class MaterialIssueSlipDetailView(generics.RetrieveAPIView):
    serializer_class = MaterialIssueSlipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaterialIssueSlip.objects.select_related(
            'job_order', 'issued_to', 'created_by', 'issued_to_worker__user',
        ).prefetch_related('items__raw_material', 'items__warehouse').all()


class PurchaseRequisitionListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseRequisition.objects.select_related(
        'job_order', 'requested_by', 'approved_by',
    ).prefetch_related('items__raw_material').all()
    serializer_class = PurchaseRequisitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department', 'job_order']
    search_fields = ['requisition_no', 'job_order__job_no', 'department']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PurchaseRequisitionDetailView(generics.RetrieveDestroyAPIView):
    queryset = PurchaseRequisition.objects.select_related(
        'job_order', 'requested_by', 'approved_by',
    ).prefetch_related('items__raw_material').all()
    serializer_class = PurchaseRequisitionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class WorkerAttendanceExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.attendance.models import Attendance

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        today = timezone.localdate()

        try:
            start = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else today
            end = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else start
        except ValueError:
            return Response(
                {
                    'detail': 'Invalid date format. Use YYYY-MM-DD.',
                    'received': {'date_from': date_from, 'date_to': date_to},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start > end:
            return Response(
                {'detail': 'date_from cannot be after date_to.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workers = Worker.objects.select_related('user').filter(
            status='active',
        ).order_by('user__first_name', 'user__last_name')

        wb = Workbook()
        wb.remove(wb.active)

        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current += timezone.timedelta(days=1)

        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            ws = wb.create_sheet(title=date_str)

            attendances = {
                att['employee_id']: att
                for att in Attendance.objects.filter(
                    date=date,
                    employee__role='production_worker',
                ).values(
                    'employee_id', 'punch_in_time', 'punch_out_time',
                )
            }

            from openpyxl.styles import Font, Alignment, Border, Side
            from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
            from openpyxl.drawing.xdr import XDRPositiveSize2D
            from openpyxl.utils.units import pixels_to_EMU

            # --------------------------------
            # HEADER
            # --------------------------------

            # --------------------------------
            # LOGO
            # --------------------------------

            # Merge logo area
            ws.merge_cells('A1:A2')

            # Path of logo
            logo_path = os.path.join(
                settings.BASE_DIR,
                'static',
                'images',
                'logo.png'
            )

            # Add logo if file exists
            if os.path.exists(logo_path):
                logo = Image(logo_path)

                # Resize logo
                logo.width = 100
                logo.height = 65

                # Center logo inside merged cell A1:A2
                column_width_px = 15 * 7 + 5
                row_height_px = int((35 + 30) * 4 / 3)

                left_offset = max(0, (column_width_px - logo.width) // 2)
                top_offset = max(0, (row_height_px - logo.height) // 2)

                logo.anchor = OneCellAnchor(
                    _from=AnchorMarker(
                        col=0,
                        colOff=pixels_to_EMU(left_offset),
                        row=0,
                        rowOff=pixels_to_EMU(top_offset),
                    ),
                    ext=XDRPositiveSize2D(
                        pixels_to_EMU(logo.width),
                        pixels_to_EMU(logo.height),
                    ),
                )
                ws.add_image(logo)


            # --------------------------------
            # COMPANY NAME
            # --------------------------------

            ws.merge_cells('B1:E1')

            ws['B1'] = 'UMA TECHNO FAB'

            ws['B1'].font = Font(
                name='Arial',
                size=16,
                bold=True
            )

            ws['B1'].alignment = Alignment(
                horizontal='center',
                vertical='center'
            )


            # --------------------------------
            # DATE
            # --------------------------------

            ws.merge_cells('B2:E2')

            ws['B2'] = f'DATE:- {date_str}'

            ws['B2'].font = Font(
                name='Arial',
                size=13,
                bold=True
            )

            ws['B2'].alignment = Alignment(
                horizontal='center',
                vertical='center'
            )


            # --------------------------------
            # TABLE HEADER
            # --------------------------------

            headers = [
                'NO.',
                'NAME',
                'IN TIME',
                'OUT TIME',
                'SIGN.'
            ]

            for col_num, header in enumerate(headers, start=1):

                cell = ws.cell(
                    row=3,
                    column=col_num
                )

                cell.value = header

                cell.font = Font(
                    name='Arial',
                    size=12,
                    bold=True
                )

                cell.alignment = Alignment(
                    horizontal='center',
                    vertical='center'
                )

            # --------------------------------
            # BORDERS
            # --------------------------------

            thin = Side(
                style='thin',
                color='000000'
            )

            border = Border(
                left=thin,
                right=thin,
                top=thin,
                bottom=thin
            )

            # Apply borders to header
            for row in ws.iter_rows(
                min_row=1,
                max_row=3,
                min_col=1,
                max_col=5
            ):
                for cell in row:
                    cell.border = border

            # Header row height
            ws.row_dimensions[1].height = 35
            ws.row_dimensions[2].height = 30
            ws.row_dimensions[3].height = 28

            row_num = 0
            for worker in workers:
                row_num += 1
                data_row = 3 + row_num
                ws.row_dimensions[data_row].height = 22

                att = attendances.get(worker.user_id)
                punch_in = ''
                punch_out = ''
                if att:
                    if att['punch_in_time']:
                        punch_in = timezone.localtime(
                            att['punch_in_time'],
                        ).strftime('%H:%M')
                    if att['punch_out_time']:
                        punch_out = timezone.localtime(
                            att['punch_out_time'],
                        ).strftime('%H:%M')

                name = worker.user.get_full_name() or worker.user.email
                ws.append([row_num, name, punch_in or '—', punch_out or '—', ''])

                for cell in ws[data_row]:
                    cell.border = border
                    cell.alignment = Alignment(
                        horizontal='center',
                        vertical='center'
                    )

            # Column widths
            ws.column_dimensions['A'].width = 15
            ws.column_dimensions['B'].width = 30
            ws.column_dimensions['C'].width = 12
            ws.column_dimensions['D'].width = 12
            ws.column_dimensions['E'].width = 14

        http_response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f'worker_attendance_{start}_{end}.xlsx'
        http_response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(http_response)
        return http_response


class WorkerProfileDailyRoutineExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        try:
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                date = timezone.localdate()
        except ValueError:
            return Response(
                {
                    'detail': 'Invalid date format. Use YYYY-MM-DD.',
                    'received': date_str,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        workers = Worker.objects.select_related('user').filter(
            status='active',
        ).order_by('user__first_name', 'user__last_name')
        worker_names = [
            worker.user.get_full_name() or worker.user.email
            for worker in workers
        ]

        wb = Workbook()
        ws = wb.active
        ws.title = 'Daily Routine'

        thin = Side(style='thin', color='000000')
        border = Border(
            left=thin, right=thin, top=thin, bottom=thin,
        )
        center = Alignment(horizontal='center', vertical='center')

        # Logo centered in merged A1:A2
        ws.merge_cells('A1:A2')
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            from openpyxl.drawing.spreadsheet_drawing import (
                AnchorMarker,
                OneCellAnchor,
            )
            from openpyxl.drawing.xdr import XDRPositiveSize2D
            from openpyxl.utils.units import pixels_to_EMU

            logo = Image(logo_path)
            logo.width = 100
            logo.height = 65

            column_width_px = 15 * 7 + 5
            row_height_px = int((35 + 30) * 4 / 3)

            left_offset = max(0, (column_width_px - logo.width) // 2)
            top_offset = max(0, (row_height_px - logo.height) // 2)

            logo.anchor = OneCellAnchor(
                _from=AnchorMarker(
                    col=0,
                    colOff=pixels_to_EMU(left_offset),
                    row=0,
                    rowOff=pixels_to_EMU(top_offset),
                ),
                ext=XDRPositiveSize2D(
                    pixels_to_EMU(logo.width),
                    pixels_to_EMU(logo.height),
                ),
            )
            ws.add_image(logo)

        # Company name
        ws.merge_cells('B1:E1')
        cell = ws['B1']
        cell.value = 'UMA TECHNO FAB'
        cell.font = Font(name='Arial', size=16, bold=True)
        cell.alignment = center

        # Title + date
        ws.merge_cells('B2:C2')
        cell = ws['B2']
        cell.value = 'WORK PROFILE DAILY RUOTINE'
        cell.font = Font(name='Arial', size=13, bold=True)
        cell.alignment = center

        ws.merge_cells('D2:E2')
        cell = ws['D2']
        cell.value = f"DATE - {date.strftime('%d-%m-%Y')}"
        cell.font = Font(name='Arial', size=11, bold=True)
        cell.alignment = Alignment(horizontal='right', vertical='center')

        # Table header
        headers = ['SL NO.', 'NAME', 'T', 'S', 'WORKER']
        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_num, value=header)
            cell.font = Font(name='Arial', size=12, bold=True)
            cell.alignment = center

        # Borders for header
        for row in ws.iter_rows(
            min_row=1,
            max_row=3,
            min_col=1,
            max_col=5,
        ):
            for cell in row:
                cell.border = border

        ws.row_dimensions[1].height = 35
        ws.row_dimensions[2].height = 30
        ws.row_dimensions[3].height = 28

        # Data rows: one row per worker from the database
        for i, name in enumerate(worker_names, start=1):
            data_row = 3 + i
            ws.row_dimensions[data_row].height = 22
            ws.append([i, name, '', '', ''])
            for cell in ws[data_row]:
                cell.border = border
                cell.alignment = center

        # Column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 14

        http_response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = (
            f"worker_profile_daily_routine_{date.strftime('%Y-%m-%d')}.xlsx"
        )
        http_response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(http_response)
        return http_response


class JobOrderProductionReportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from apps.production.models import MaterialRequirement

        try:
            job_order = JobOrder.objects.select_related(
                'sales_order', 'quotation', 'customer', 'product',
                'machine', 'supervisor', 'bom',
            ).prefetch_related('processes').get(pk=pk)
        except JobOrder.DoesNotExist:
            return Response(
                {'detail': 'Job order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        from apps.production.models import Dispatch
        dispatch = Dispatch.objects.filter(
            job_order=job_order,
        ).exclude(dispatch_date__isnull=True).order_by('-dispatch_date').first()
        if not dispatch:
            dispatch = Dispatch.objects.filter(
                job_order=job_order,
            ).order_by('-id').first()

        requirements = MaterialRequirement.objects.filter(
            job_order=job_order,
        ).select_related('raw_material')

        # Dynamic process columns: only the processes belonging to this job order.
        # Fall back to active production stages if the job has no processes yet.
        processes = list(
            job_order.processes.all().order_by('sequence'),
        )
        if processes:
            process_headers = [name.upper() for name in
                               [p.name for p in processes] if name]
        else:
            process_headers = [
                name.upper() for name in ProductionStage.objects.filter(
                    is_active=True,
                ).order_by('sequence').values_list('name', flat=True)
            ]

        total_cols = 5 + len(process_headers) + 1  # fixed cols + processes + REMARK

        def fmt_date(value):
            return value.strftime('%d-%m-%Y') if value else ''

        starting_date = fmt_date(job_order.start_date)
        dispatched_date = fmt_date(dispatch.dispatch_date) if dispatch else ''
        req_delivery_date = fmt_date(
            job_order.quotation.delivery_date,
        ) if job_order.quotation else ''
        client_name = job_order.customer.name if job_order.customer else ''
        supervisor_name = (
            job_order.supervisor.get_full_name() or job_order.supervisor.email
        ) if job_order.supervisor else ''
        dr_no = dispatch.dispatch_no if dispatch else ''
        job_name = job_order.product.name if job_order.product else ''
        filter_name = ''
        if job_order.product and job_order.product.specifications:
            filter_name = job_order.product.specifications.get('filter', '')

        wb = Workbook()
        ws = wb.active
        ws.title = 'Production Report'

        thin = Side(style='thin', color='000000')
        border = Border(
            left=thin, right=thin, top=thin, bottom=thin,
        )
        center = Alignment(horizontal='center', vertical='center')
        left_align = Alignment(horizontal='left', vertical='center')

        def set_cell(row, col, value, font=None, align=None, bd=None):
            cell = ws.cell(row=row, column=col, value=value)
            if font:
                cell.font = font
            if align:
                cell.alignment = align
            if bd:
                cell.border = bd
            return cell

        title_font = Font(name='Arial', size=16, bold=True)
        section_font = Font(name='Arial', size=11, bold=True)
        normal_font = Font(name='Arial', size=11)
        header_font = Font(name='Arial', size=11, bold=True)

        last_col_letter = get_column_letter(total_cols)

        # Logo centered in merged A1:A2
        ws.merge_cells('A1:A2')
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            from openpyxl.drawing.spreadsheet_drawing import (
                AnchorMarker,
                OneCellAnchor,
            )
            from openpyxl.drawing.xdr import XDRPositiveSize2D
            from openpyxl.utils.units import pixels_to_EMU

            logo = Image(logo_path)
            logo.width = 100
            logo.height = 65

            column_width_px = 19 * 7 + 5
            row_height_px = int((35 + 30) * 4 / 3)

            left_offset = max(0, (column_width_px - logo.width) // 2)
            top_offset = max(0, (row_height_px - logo.height) // 2)

            logo.anchor = OneCellAnchor(
                _from=AnchorMarker(
                    col=0,
                    colOff=pixels_to_EMU(left_offset),
                    row=0,
                    rowOff=pixels_to_EMU(top_offset),
                ),
                ext=XDRPositiveSize2D(
                    pixels_to_EMU(logo.width),
                    pixels_to_EMU(logo.height),
                ),
            )
            ws.add_image(logo)

        # Company name merged across remaining columns of row 1
        ws.merge_cells(
            start_row=1, start_column=2,
            end_row=1, end_column=total_cols - 1,
        )
        set_cell(
            1, 2, 'UMA TECHNO FAB', font=title_font,
            align=Alignment(horizontal='center', vertical='center'),
        )
        set_cell(
            1, total_cols, 'Doc No.: F-PRD-04', font=section_font,
            align=Alignment(horizontal='right', vertical='center'),
        )

        # Title merged across remaining columns of row 2
        ws.merge_cells(
            start_row=2, start_column=2,
            end_row=2, end_column=total_cols,
        )
        set_cell(
            2, 2, 'Production Report',
            font=Font(name='Arial', size=14, bold=True),
            align=center,
        )

        # Rows 3-5: three info sections of three fields each.
        # Label + value in separate cells aligned with the first five table
        # columns so the info section never distorts the process columns.
        bottom_only = Border(
            bottom=Side(style='thin', color='000000'),
        )
        info_rows = [
            ('STARTING DATE', starting_date, 'CLIENT NAME', client_name,
             'DISPATCHED DATE', dispatched_date),
            ('Req Delivery Date', req_delivery_date, 'Fiter Name', filter_name,
             'Supervisor Name', supervisor_name),
            ('DR. NO.', dr_no, 'JOB. NAME.', job_name, 'JOB NO.', job_order.job_no),
        ]
        for i, (l1, v1, l2, v2, l3, v3) in enumerate(info_rows, start=3):
            set_cell(i, 1, l1, font=section_font, align=center, bd=bottom_only)
            set_cell(i, 2, str(v1), font=normal_font, align=left_align, bd=bottom_only)
            set_cell(i, 3, l2, font=section_font, align=center, bd=bottom_only)
            set_cell(i, 4, str(v2), font=normal_font, align=left_align, bd=bottom_only)
            set_cell(i, 5, l3, font=section_font, align=center, bd=bottom_only)
            set_cell(i, 6, str(v3), font=normal_font, align=left_align, bd=bottom_only)

        # Table header (rows 6-7): fixed columns on top, a merged PROCESS NAME
        # row spanning the process columns, and the process names below.
        for col in range(1, total_cols + 1):
            set_cell(6, col, '', bd=border)
            set_cell(7, col, '', bd=border)

        fixed_cols = [1, 2, 3, 4, 5]
        fixed_headers = ['SR.', 'DISCRIPTION', 'SIZE', 'QTY', 'MAT']
        for col, name in zip(fixed_cols, fixed_headers):
            ws.merge_cells(
                start_row=6, start_column=col,
                end_row=7, end_column=col,
            )
            set_cell(6, col, name, font=header_font, align=center, bd=border)

        ws.merge_cells(
            start_row=6, start_column=total_cols,
            end_row=7, end_column=total_cols,
        )
        set_cell(6, total_cols, 'REMARK', font=header_font, align=center, bd=border)

        if process_headers:
            if total_cols - 1 > 6:
                ws.merge_cells(
                    start_row=6, start_column=6,
                    end_row=6, end_column=total_cols - 1,
                )
            set_cell(6, 6, 'PROCESS NAME', font=header_font, align=center, bd=border)
            for idx, name in enumerate(process_headers):
                set_cell(7, 6 + idx, name, font=header_font, align=center, bd=border)

        ws.row_dimensions[6].height = 22
        ws.row_dimensions[7].height = 20

        # Rows 8+ : material requirements, padded to 27 rows
        data_start = 8
        max_rows = max(len(requirements), 27)
        for idx, req in enumerate(requirements):
            row = data_start + idx
            size = ''
            if req.raw_material.specifications:
                size = req.raw_material.specifications.get('size', '')
            set_cell(row, 1, str(idx + 1), align=center, bd=border)
            set_cell(row, 2, req.raw_material.name, align=left_align, bd=border)
            set_cell(row, 3, size, align=center, bd=border)
            set_cell(row, 4, str(req.required_quantity), align=center, bd=border)
            set_cell(row, 5, req.raw_material.unit, align=center, bd=border)
            for c in range(6, total_cols):
                set_cell(row, c, '', align=center, bd=border)
            set_cell(row, total_cols, '', align=left_align, bd=border)
            ws.row_dimensions[row].height = 20

        for row in range(data_start + len(requirements), data_start + max_rows):
            for col in range(1, total_cols + 1):
                set_cell(row, col, '', bd=border)
            ws.row_dimensions[row].height = 20

        # Column widths: size each column to its longest value.
        # Column A stays fixed so the logo stays centered in it.
        last_row = data_start + max_rows - 1
        table_widths = {}
        for col in range(1, total_cols + 1):
            w = 0
            row_start = 7 if 6 <= col <= total_cols - 1 else 6
            for row in range(row_start, last_row + 1):
                v = ws.cell(row=row, column=col).value
                if v is not None:
                    w = max(w, sum(2 if ord(ch) > 127 else 1 for ch in str(v)))
            table_widths[col] = w

        widths = {'A': 19}
        for col in range(2, total_cols + 1):
            if 2 <= col <= 5:
                info_w = 0
                for row in range(3, 6):
                    v = ws.cell(row=row, column=col).value
                    if v is not None:
                        info_w = max(info_w, sum(
                            2 if ord(ch) > 127 else 1 for ch in str(v)
                        ))
                content = max(table_widths[col], info_w)
            else:
                content = table_widths[col]
            if col == total_cols:
                content = max(content, len('Doc No.: F-PRD-04'))
            min_w = 8 if col <= 5 else 10
            widths[get_column_letter(col)] = max(
                min_w, min(content + 2, 60),
            )
        for letter, width in widths.items():
            ws.column_dimensions[letter].width = width

        # Row heights
        ws.row_dimensions[1].height = 35
        ws.row_dimensions[2].height = 30

        http_response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f'production_report_{job_order.job_no}.xlsx'
        http_response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(http_response)
        return http_response


class PurchaseRequisitionApproveView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def post(self, request, pk):
        requisition = PurchaseRequisition.objects.get(pk=pk)
        try:
            purchase_order = services.approve_purchase_requisition(
                requisition, approved_by=request.user,
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        requisition.refresh_from_db()
        return Response({
            'requisition': PurchaseRequisitionSerializer(requisition).data,
            'purchase_order_id': purchase_order.purchase_order_id,
        }, status=status.HTTP_200_OK)


class PurchaseRequisitionRejectView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def post(self, request, pk):
        requisition = PurchaseRequisition.objects.get(pk=pk)
        services.reject_purchase_requisition(
            requisition, approved_by=request.user,
        )
        requisition.refresh_from_db()
        return Response(
            PurchaseRequisitionSerializer(requisition).data,
            status=status.HTTP_200_OK,
        )


class GoodsReceiptNoteListCreateView(generics.ListCreateAPIView):
    queryset = GoodsReceiptNote.objects.select_related(
        'purchase_order', 'supplier', 'warehouse', 'received_by',
    ).prefetch_related('items__product').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'warehouse', 'purchase_order']
    search_fields = ['grn_no', 'supplier__name', 'purchase_order__purchase_order_id']
    ordering_fields = ['received_date', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GoodsReceiptNoteCreateSerializer
        return GoodsReceiptNoteSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grn = serializer.save(received_by=request.user)
        return Response(
            GoodsReceiptNoteSerializer(grn).data,
            status=status.HTTP_201_CREATED,
        )


class GoodsReceiptNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GoodsReceiptNote.objects.select_related(
        'purchase_order', 'supplier', 'warehouse', 'received_by',
    ).prefetch_related('items__product').all()
    serializer_class = GoodsReceiptNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class GoodsReceiptNoteReceiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        grn = GoodsReceiptNote.objects.get(pk=pk)
        try:
            grn = services.receive_grn(grn)
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        grn.refresh_from_db()
        return Response(
            GoodsReceiptNoteSerializer(grn).data, status=status.HTTP_200_OK,
        )


class GoodsReceiptNoteInspectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        grn = GoodsReceiptNote.objects.get(pk=pk)
        items = list(grn.items.select_related('product').all())
        if not items:
            return Response(
                {'detail': 'GRN has no items to inspect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inspections = []
        for item in items:
            inspections.append(QualityInspection.objects.create(
                grn=grn,
                product=item.product,
                quantity=item.quantity,
                status='pending',
            ))
        return Response(
            QualityInspectionSerializer(inspections, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class QualityInspectionListCreateView(generics.ListCreateAPIView):
    queryset = QualityInspection.objects.select_related(
        'grn', 'job_order', 'product', 'inspected_by',
    ).all()
    serializer_class = QualityInspectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'grn', 'job_order', 'product']
    search_fields = ['inspection_no', 'grn__grn_no', 'job_order__job_no']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class QualityInspectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QualityInspection.objects.select_related(
        'grn', 'job_order', 'product', 'inspected_by',
    ).all()
    serializer_class = QualityInspectionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class QualityInspectionResultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        inspection = QualityInspection.objects.get(pk=pk)
        passed = bool(request.data.get('passed', True))
        try:
            inspection = services.finalize_inspection(
                inspection,
                passed=passed,
                inspected_by=request.user,
                notes=request.data.get('notes'),
            )
        except ValueError as exc:
            return Response(
                {'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST,
            )
        inspection.refresh_from_db()
        return Response(
            QualityInspectionSerializer(inspection).data,
            status=status.HTTP_200_OK,
        )


class ProductionProcessListView(generics.ListAPIView):
    serializer_class = ProductionProcessSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['job_order', 'status', 'name']
    ordering_fields = ['sequence', 'status']

    def get_queryset(self):
        return ProductionProcess.objects.filter(
            job_order_id=self.request.query_params.get('job_order'),
        ) if self.request.query_params.get('job_order') else ProductionProcess.objects.all()


class ProductionProcessAdvanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            process = ProductionProcess.objects.get(pk=pk)
        except ProductionProcess.DoesNotExist:
            return Response(
                {'detail': 'Production process not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        worker = request.data.get('worker')
        if worker is not None and worker != '':
            process.worker_id = worker
            process.save(update_fields=['worker'])
        process = services.advance_process(process)
        return Response(
            ProductionProcessSerializer(process).data,
            status=status.HTTP_200_OK,
        )


class FinishedGoodsListView(generics.ListAPIView):
    serializer_class = FinishedGoodsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_order', 'product', 'warehouse', 'status']
    search_fields = ['finished_goods_no', 'batch_no', 'barcode', 'product__name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return FinishedGoods.objects.select_related(
            'job_order', 'product', 'warehouse',
        ).all()


class FinishedGoodsDetailView(generics.RetrieveAPIView):
    queryset = FinishedGoods.objects.select_related(
        'job_order', 'product', 'warehouse',
    ).all()
    serializer_class = FinishedGoodsSerializer
    permission_classes = [IsAuthenticated]


class DispatchListCreateView(generics.ListCreateAPIView):
    queryset = Dispatch.objects.select_related(
        'job_order', 'sales_order', 'customer', 'delivery_note',
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'job_order', 'sales_order']
    search_fields = ['dispatch_no', 'vehicle_number', 'driver_name']
    ordering_fields = ['created_at', 'dispatch_date']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DispatchCreateSerializer
        return DispatchSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class DispatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dispatch.objects.select_related(
        'job_order', 'sales_order', 'customer', 'delivery_note',
    ).all()
    serializer_class = DispatchSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class DispatchMarkDispatchedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        dispatch = Dispatch.objects.get(pk=pk)
        dispatch = services.mark_dispatch_dispatched(
            dispatch,
            vehicle_number=request.data.get('vehicle_number', ''),
            driver_name=request.data.get('driver_name', ''),
            driver_phone=request.data.get('driver_phone', ''),
        )
        return Response(
            DispatchSerializer(dispatch).data, status=status.HTTP_200_OK,
        )


class WorkerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['worker_type', 'skill_level', 'status', 'machine']
    search_fields = [
        'worker_code', 'user__first_name', 'user__last_name', 'user__email',
        'user__phone',
    ]
    ordering_fields = ['created_at', 'worker_code']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkerCreateSerializer
        return WorkerSerializer

    def get_queryset(self):
        return Worker.objects.select_related(
            'user', 'machine',
        ).all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worker = serializer.save()
        return Response(
            WorkerSerializer(worker).data,
            status=status.HTTP_201_CREATED,
        )


class WorkerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worker.objects.select_related(
        'user', 'machine',
    ).all()
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class DailyWorkEntryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['worker', 'date', 'job_order']
    search_fields = [
        'worker__user__first_name', 'worker__user__last_name',
        'worker__user__email', 'description', 'remarks',
    ]
    ordering_fields = ['date', 'quantity', 'hours', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DailyWorkEntryCreateSerializer
        return DailyWorkEntrySerializer

    def get_queryset(self):
        qs = DailyWorkEntry.objects.select_related(
            'worker__user', 'job_order',
        ).all()
        if self.request.user.role not in ['super_admin', 'manager']:
            profile = getattr(
                self.request.user, 'production_worker_profile', None,
            )
            qs = qs.filter(worker=profile) if profile else qs.none()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        worker = getattr(request.user, 'production_worker_profile', None)
        if worker is None:
            return Response(
                {'detail': 'Worker profile not found for this user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.validated_data['worker'] = worker
        entry = serializer.save()
        return Response(
            DailyWorkEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class DailyWorkEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyWorkEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DailyWorkEntryCreateSerializer
        return DailyWorkEntrySerializer

    def get_queryset(self):
        qs = DailyWorkEntry.objects.select_related(
            'worker__user', 'job_order',
        ).all()
        if self.request.user.role not in ['super_admin', 'manager']:
            profile = getattr(
                self.request.user, 'production_worker_profile', None,
            )
            qs = qs.filter(worker=profile) if profile else qs.none()
        return qs

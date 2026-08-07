from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from . import services
from .models import (
    Bom,
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
)
from .serializers import (
    BomCreateSerializer,
    BomSerializer,
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
        'operators', 'material_requirements__raw_material',
        'processes', 'finished_goods',
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
        'operators', 'material_requirements__raw_material',
        'processes', 'finished_goods',
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
        job_order = services.start_production(
            job_order,
            machine=request.data.get('machine'),
            supervisor=request.data.get('supervisor'),
            operators=request.data.get('operators'),
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
            'job_order', 'issued_to', 'created_by',
        ).prefetch_related('items__raw_material', 'items__warehouse').all()


class MaterialIssueSlipDetailView(generics.RetrieveAPIView):
    serializer_class = MaterialIssueSlipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaterialIssueSlip.objects.select_related(
            'job_order', 'issued_to', 'created_by',
        ).prefetch_related('items__raw_material', 'items__warehouse').all()


class PurchaseRequisitionListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseRequisition.objects.select_related(
        'job_order', 'requested_by', 'approved_by',
    ).prefetch_related('items__raw_material').all()
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
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


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
        process = ProductionProcess.objects.get(pk=pk)
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

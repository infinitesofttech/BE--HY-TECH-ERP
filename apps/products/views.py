from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    ProductCategory, Product, TourPlan, Policy, Warehouse, Supplier, Inventory,
    StockAdjustment, StockTransfer, adjust_inventory,
)
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductCreateSerializer,
    ProductCatalogueSerializer,
    TourPlanSerializer,
    PolicySerializer,
    WarehouseSerializer,
    SupplierSerializer,
    InventorySerializer,
    StockAdjustmentSerializer,
    StockTransferSerializer,
)
from apps.accounts.permissions import IsSuperAdmin


class ProductCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class ProductCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class ProductListCreateView(generics.ListCreateAPIView):
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'for_vehicle_type', 'status', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        return Product.objects.select_related('category').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProductCreateSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class ProductToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        return Response({
            'detail': f'Product {"activated" if product.is_active else "deactivated"} successfully.',
            'is_active': product.is_active,
        }, status=status.HTTP_200_OK)


class ProductCatalogueView(APIView):
    permission_classes = []

    def get(self, request):
        from django.db.models import Q
        products = Product.objects.select_related('category').filter(
            is_active=True,
        )
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            products = products.filter(
                Q(for_vehicle_type=vehicle_type)
                | Q(for_vehicle_type='both')
            )
        grouped = {}
        for product in products:
            cat_name = product.category.name
            if cat_name not in grouped:
                grouped[cat_name] = {
                    'category_id': product.category.id,
                    'category_name': cat_name,
                    'products': [],
                }
            grouped[cat_name]['products'].append(
                ProductCatalogueSerializer(product).data,
            )
        return Response(list(grouped.values()), status=status.HTTP_200_OK)


class TourPlanListCreateView(generics.ListCreateAPIView):
    queryset = TourPlan.objects.all()
    serializer_class = TourPlanSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class TourPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TourPlan.objects.all()
    serializer_class = TourPlanSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class TourPlanToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            plan = TourPlan.objects.get(pk=pk)
        except TourPlan.DoesNotExist:
            return Response(
                {'detail': 'Tour plan not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        plan.is_active = not plan.is_active
        plan.save(update_fields=['is_active'])
        return Response({
            'detail': f'Tour plan {"activated" if plan.is_active else "deactivated"} successfully.',
            'is_active': plan.is_active,
        }, status=status.HTTP_200_OK)


class PolicyListCreateView(generics.ListCreateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class PolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class PolicyToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            policy = Policy.objects.get(pk=pk)
        except Policy.DoesNotExist:
            return Response(
                {'detail': 'Policy not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        policy.is_active = not policy.is_active
        policy.save(update_fields=['is_active'])
        return Response({
            'detail': f'Policy {"activated" if policy.is_active else "deactivated"} successfully.',
            'is_active': policy.is_active,
        }, status=status.HTTP_200_OK)


class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'contact_person', 'phone']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class WarehouseToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            warehouse = Warehouse.objects.get(pk=pk)
        except Warehouse.DoesNotExist:
            return Response(
                {'detail': 'Warehouse not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        warehouse.status = 'inactive' if warehouse.status == 'active' else 'active'
        warehouse.save(update_fields=['status'])
        return Response({
            'detail': f'Warehouse {"activated" if warehouse.status == "active" else "deactivated"} successfully.',
            'status': warehouse.status,
        }, status=status.HTTP_200_OK)


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'country']
    search_fields = ['name', 'email', 'phone', 'country']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class SupplierToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return Response(
                {'detail': 'Supplier not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        supplier.status = 'inactive' if supplier.status == 'active' else 'active'
        supplier.save(update_fields=['status'])
        return Response({
            'detail': f'Supplier {"activated" if supplier.status == "active" else "deactivated"} successfully.',
            'status': supplier.status,
        }, status=status.HTTP_200_OK)


class InventoryListCreateView(generics.ListCreateAPIView):
    queryset = Inventory.objects.select_related('product', 'warehouse').all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'warehouse', 'status']
    search_fields = ['product__name', 'warehouse__name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.select_related('product', 'warehouse').all()
    serializer_class = InventorySerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []


class InventoryToggleActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            inventory = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response(
                {'detail': 'Inventory not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        inventory.status = 'inactive' if inventory.status == 'active' else 'active'
        inventory.save(update_fields=['status'])
        return Response({
            'detail': f'Inventory {"activated" if inventory.status == "active" else "deactivated"} successfully.',
            'status': inventory.status,
        }, status=status.HTTP_200_OK)


class StockAdjustmentListCreateView(generics.ListCreateAPIView):
    queryset = StockAdjustment.objects.select_related(
        'product', 'warehouse',
    ).all()
    serializer_class = StockAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'warehouse', 'reason']
    search_fields = ['product__name', 'warehouse__name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class StockAdjustmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockAdjustment.objects.select_related(
        'product', 'warehouse',
    ).all()
    serializer_class = StockAdjustmentSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []

    def perform_destroy(self, instance):
        with transaction.atomic():
            adjust_inventory(
                instance.product, instance.warehouse, -instance.difference,
            )
            instance.delete()


class StockTransferListCreateView(generics.ListCreateAPIView):
    queryset = StockTransfer.objects.select_related(
        'product', 'from_warehouse', 'to_warehouse',
    ).all()
    serializer_class = StockTransferSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['product', 'from_warehouse', 'to_warehouse', 'status']
    search_fields = ['product__name', 'from_warehouse__name', 'to_warehouse__name']
    ordering_fields = ['transfer_date', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return []


class StockTransferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockTransfer.objects.select_related(
        'product', 'from_warehouse', 'to_warehouse',
    ).all()
    serializer_class = StockTransferSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsSuperAdmin()]
        return []

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.reverse_stock()
            instance.delete()

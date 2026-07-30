from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, Product, TourPlan, Policy
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductCreateSerializer,
    ProductCatalogueSerializer,
    TourPlanSerializer,
    PolicySerializer,
)
from apps.accounts.permissions import IsSuperAdmin


class ProductCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

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

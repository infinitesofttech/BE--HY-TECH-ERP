from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from .models import Estimation, EstimationItem, Proposal
from .serializers import (
    EstimationSerializer, EstimationItemCreateSerializer,
    ProposalSerializer, ProposalCreateSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


class EstimationListCreateView(generics.ListCreateAPIView):
    queryset = Estimation.objects.prefetch_related('items').all()
    serializer_class = EstimationSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status']
    search_fields = ['customer_name', 'estimation_number', 'title']
    ordering_fields = ['created_at', 'total', 'valid_until']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        customer_name = self.request.query_params.get('customer_name')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if customer_name:
            qs = qs.filter(customer_name__icontains=customer_name)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        return qs

    @extend_schema(request=EstimationSerializer, responses={201: EstimationSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        items_data = self.request.data.get('items', [])
        validated_items = []
        for item in items_data:
            item_ser = EstimationItemCreateSerializer(data=item)
            item_ser.is_valid(raise_exception=True)
            validated_items.append(item_ser.validated_data)
        serializer.save(created_by=self.request.user, items_data=validated_items)


class EstimationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estimation.objects.prefetch_related('items').all()
    serializer_class = EstimationSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        items_data = request.data.get('items', None)
        validated_items = None
        if items_data is not None:
            validated_items = []
            for item in items_data:
                item_ser = EstimationItemCreateSerializer(data=item)
                item_ser.is_valid(raise_exception=True)
                validated_items.append(item_ser.validated_data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(items_data=validated_items)
        return Response(serializer.data)

    @extend_schema(request=EstimationSerializer, responses={200: EstimationSerializer})
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(request=EstimationSerializer, responses={200: EstimationSerializer})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ProposalListCreateView(generics.ListCreateAPIView):
    queryset = Proposal.objects.all()
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status']
    search_fields = ['customer_name', 'proposal_number', 'title']
    ordering_fields = ['created_at', 'total_amount', 'valid_until']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProposalCreateSerializer
        return ProposalSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_name = self.request.query_params.get('customer_name')
        if customer_name:
            qs = qs.filter(customer_name__icontains=customer_name)
        return qs

    @extend_schema(request=ProposalSerializer, responses={201: ProposalSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @extend_schema(request=ProposalSerializer, responses={200: ProposalSerializer})
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(request=ProposalSerializer, responses={200: ProposalSerializer})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

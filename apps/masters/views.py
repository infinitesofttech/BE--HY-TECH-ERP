from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Dealer, Retailer, Mechanic, TaxRate, Currency, Source, Industry
from .serializers import (
    DealerSerializer, RetailerSerializer, MechanicSerializer,
    TaxRateSerializer, CurrencySerializer, SourceSerializer, IndustrySerializer,
)
from apps.accounts.permissions import IsSuperAdmin, IsManagerOrAbove


class ListCreateMixin:
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class DetailMixin:
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class TaxRateListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer

    @extend_schema(request=TaxRateSerializer, responses={201: TaxRateSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaxRateDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer


class CurrencyListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    @extend_schema(request=CurrencySerializer, responses={201: CurrencySerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CurrencyDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class SourceListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

    @extend_schema(request=SourceSerializer, responses={201: SourceSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SourceDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class IndustryListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

    @extend_schema(request=IndustrySerializer, responses={201: IndustrySerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class IndustryDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


class DealerListCreateView(generics.ListCreateAPIView):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'city', 'pin_code', 'assigned_to']
    search_fields = ['name', 'contact_person', 'city', 'pin_code']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class DealerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class DealerToggleStatusView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def patch(self, request, pk):
        try:
            dealer = Dealer.objects.get(pk=pk)
        except Dealer.DoesNotExist:
            return Response({'error': 'Dealer not found'}, status=404)
        dealer.status = 'inactive' if dealer.status == 'active' else 'active'
        dealer.save()
        return Response({'status': dealer.status})


class RetailerListCreateView(generics.ListCreateAPIView):
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'city', 'pin_code', 'assigned_to']
    search_fields = ['name', 'contact_person', 'city', 'pin_code']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class RetailerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class RetailerToggleStatusView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def patch(self, request, pk):
        try:
            retailer = Retailer.objects.get(pk=pk)
        except Retailer.DoesNotExist:
            return Response({'error': 'Retailer not found'}, status=404)
        retailer.status = 'inactive' if retailer.status == 'active' else 'active'
        retailer.save()
        return Response({'status': retailer.status})


class MechanicListCreateView(generics.ListCreateAPIView):
    queryset = Mechanic.objects.all()
    serializer_class = MechanicSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'city', 'pin_code', 'assigned_to']
    search_fields = ['name', 'contact_person', 'city', 'pin_code']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class MechanicDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mechanic.objects.all()
    serializer_class = MechanicSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class MechanicToggleStatusView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def patch(self, request, pk):
        try:
            mechanic = Mechanic.objects.get(pk=pk)
        except Mechanic.DoesNotExist:
            return Response({'error': 'Mechanic not found'}, status=404)
        mechanic.status = 'inactive' if mechanic.status == 'active' else 'active'
        mechanic.save()
        return Response({'status': mechanic.status})

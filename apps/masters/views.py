from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import (
    Dealer, Retailer, Currency, Source, Industry,
    ContactStage, LostReason, CallReason, CallLog,
)
from .serializers import (
    DealerSerializer, RetailerSerializer,
    CurrencySerializer, SourceSerializer, IndustrySerializer,
    ContactStageSerializer, LostReasonSerializer, CallReasonSerializer, CallLogSerializer,
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


class ContactStageListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = ContactStage.objects.all()
    serializer_class = ContactStageSerializer

    @extend_schema(request=ContactStageSerializer, responses={201: ContactStageSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ContactStageDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactStage.objects.all()
    serializer_class = ContactStageSerializer


class LostReasonListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = LostReason.objects.all()
    serializer_class = LostReasonSerializer

    @extend_schema(request=LostReasonSerializer, responses={201: LostReasonSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LostReasonDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LostReason.objects.all()
    serializer_class = LostReasonSerializer


class CallReasonListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = CallReason.objects.all()
    serializer_class = CallReasonSerializer

    @extend_schema(request=CallReasonSerializer, responses={201: CallReasonSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CallReasonDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CallReason.objects.all()
    serializer_class = CallReasonSerializer


class CallLogListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    @extend_schema(request=CallLogSerializer, responses={201: CallLogSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CallLogDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer

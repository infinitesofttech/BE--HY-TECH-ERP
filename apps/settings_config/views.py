from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import (
    Department, Designation, CustomField, PrefixSetting,
    PrinterSetting, GDPRConsent, LocalizationSetting,
    LanguageSetting, AppearanceSetting, InvoiceSetting, SecuritySetting,
    Country, SmsGateway, EmailSetting, StorageSetting, SystemUpdate, NotificationSetting,
)
from .serializers import (
    DepartmentSerializer, DepartmentCreateSerializer,
    DesignationSerializer, DesignationCreateSerializer,
    CustomFieldSerializer, CustomFieldCreateSerializer,
    PrefixSettingSerializer, PrinterSettingSerializer,
    GDPRConsentSerializer, LocalizationSettingSerializer,
    LanguageSettingSerializer, AppearanceSettingSerializer,
    InvoiceSettingSerializer, SecuritySettingSerializer,
    CountrySerializer, SmsGatewaySerializer, EmailSettingSerializer,
    StorageSettingSerializer, SystemUpdateSerializer, NotificationSettingSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


class ListCreateMixin:
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return getattr(self, 'create_serializer_class', self.serializer_class)
        return self.serializer_class


class DetailMixin:
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class SingleTonMixin:
    permission_classes = [IsAuthenticated]

    def get_object(self):
        instance, _ = self.model.objects.get_or_create(pk=1, defaults=self.defaults)
        return instance

    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().put(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class DepartmentListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = Department.objects.select_related('department_head').annotate(
        employee_count=Count('employees'),
    ).order_by('-id')
    serializer_class = DepartmentSerializer
    create_serializer_class = DepartmentCreateSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'department_head']
    search_fields = ['name', 'description', 'department_head__email', 'department_head__first_name']
    ordering_fields = ['name', 'created_at']


class DepartmentDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.select_related('department_head').annotate(
        employee_count=Count('employees'),
    ).all()
    serializer_class = DepartmentSerializer


class DesignationListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = Designation.objects.select_related('department').annotate(
        employee_count=Count('employees'),
    ).order_by('-id')
    serializer_class = DesignationSerializer
    create_serializer_class = DesignationCreateSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'department']
    search_fields = ['name', 'department__name']
    ordering_fields = ['name', 'created_at']


class DesignationDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Designation.objects.select_related('department').annotate(
        employee_count=Count('employees'),
    ).all()
    serializer_class = DesignationSerializer


class CustomFieldListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    create_serializer_class = CustomFieldCreateSerializer


class CustomFieldDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer


class PrefixSettingListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = PrefixSetting.objects.all()
    serializer_class = PrefixSettingSerializer


class PrefixSettingDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = PrefixSetting.objects.all()
    serializer_class = PrefixSettingSerializer


class PrefixSettingNextNumberView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def patch(self, request, pk):
        try:
            prefix = PrefixSetting.objects.get(pk=pk)
        except PrefixSetting.DoesNotExist:
            return Response({'error': 'Prefix setting not found'}, status=status.HTTP_404_NOT_FOUND)
        prefix.next_number += 1
        prefix.save()
        return Response(PrefixSettingSerializer(prefix).data)


class PrinterSettingListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = PrinterSetting.objects.all()
    serializer_class = PrinterSettingSerializer


class PrinterSettingDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = PrinterSetting.objects.all()
    serializer_class = PrinterSettingSerializer


class GDPRConsentListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = GDPRConsent.objects.all()
    serializer_class = GDPRConsentSerializer


class LocalizationSettingView(SingleTonMixin, generics.RetrieveUpdateAPIView):
    model = LocalizationSetting
    serializer_class = LocalizationSettingSerializer
    defaults = {}


class LanguageSettingListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = LanguageSetting.objects.all()
    serializer_class = LanguageSettingSerializer


class LanguageSettingDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LanguageSetting.objects.all()
    serializer_class = LanguageSettingSerializer


class AppearanceSettingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        obj, _ = AppearanceSetting.objects.get_or_create(
            user=request.user,
            defaults={'user': request.user},
        )
        return Response(AppearanceSettingSerializer(obj).data)

    def put(self, request):
        obj, _ = AppearanceSetting.objects.get_or_create(
            user=request.user,
            defaults={'user': request.user},
        )
        serializer = AppearanceSettingSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InvoiceSettingView(SingleTonMixin, generics.RetrieveUpdateAPIView):
    model = InvoiceSetting
    serializer_class = InvoiceSettingSerializer
    defaults = {}


class SecuritySettingView(SingleTonMixin, generics.RetrieveUpdateAPIView):
    model = SecuritySetting
    serializer_class = SecuritySettingSerializer
    defaults = {}


class CountryListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CountryDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class SmsGatewayListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = SmsGateway.objects.all()
    serializer_class = SmsGatewaySerializer


class SmsGatewayDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = SmsGateway.objects.all()
    serializer_class = SmsGatewaySerializer


class EmailSettingView(SingleTonMixin, generics.RetrieveUpdateAPIView):
    model = EmailSetting
    serializer_class = EmailSettingSerializer
    defaults = {}


class StorageSettingView(SingleTonMixin, generics.RetrieveUpdateAPIView):
    model = StorageSetting
    serializer_class = StorageSettingSerializer
    defaults = {}


class SystemUpdateView(SingleTonMixin, generics.RetrieveUpdateAPIView):
    model = SystemUpdate
    serializer_class = SystemUpdateSerializer
    defaults = {}


class NotificationSettingListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = NotificationSetting.objects.all()
    serializer_class = NotificationSettingSerializer


class NotificationSettingDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = NotificationSetting.objects.all()
    serializer_class = NotificationSettingSerializer

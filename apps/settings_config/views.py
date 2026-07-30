from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Department, State, City, CustomField, PrefixSetting,
    PrinterSetting, GDPRConsent, LocalizationSetting,
    LanguageSetting, AppearanceSetting, InvoiceSetting, SecuritySetting,
)
from .serializers import (
    DepartmentSerializer, DepartmentCreateSerializer,
    StateSerializer, CitySerializer, CityCreateSerializer,
    CustomFieldSerializer, CustomFieldCreateSerializer,
    PrefixSettingSerializer, PrinterSettingSerializer,
    GDPRConsentSerializer, LocalizationSettingSerializer,
    LanguageSettingSerializer, AppearanceSettingSerializer,
    InvoiceSettingSerializer, SecuritySettingSerializer,
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
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    create_serializer_class = DepartmentCreateSerializer


class DepartmentDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class StateListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer


class StateDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer


class CityListCreateView(ListCreateMixin, generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    create_serializer_class = CityCreateSerializer


class CityDetailView(DetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


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

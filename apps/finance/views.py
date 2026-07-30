from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsManagerOrAbove

from .models import BankAccount, PurchaseTransaction, PaymentGateway, DiscountRule
from .serializers import (
    BankAccountSerializer, BankAccountCreateSerializer,
    PurchaseTransactionSerializer, PurchaseTransactionCreateSerializer,
    PaymentGatewaySerializer,
    DiscountRuleSerializer, DiscountRuleCreateSerializer,
)


class BankAccountListCreateView(generics.ListCreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BankAccountCreateSerializer
        return BankAccountSerializer


class BankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankAccount.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return BankAccountCreateSerializer
        return BankAccountSerializer


class PurchaseTransactionListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseTransaction.objects.select_related('created_by').all()
    serializer_class = PurchaseTransactionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseTransactionCreateSerializer
        return PurchaseTransactionSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs


class PurchaseTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseTransaction.objects.select_related('created_by').all()
    serializer_class = PurchaseTransactionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PurchaseTransactionCreateSerializer
        return PurchaseTransactionSerializer

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class PaymentGatewayListCreateView(generics.ListCreateAPIView):
    queryset = PaymentGateway.objects.all()
    serializer_class = PaymentGatewaySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PaymentGatewayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentGateway.objects.all()
    serializer_class = PaymentGatewaySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class DiscountRuleListCreateView(generics.ListCreateAPIView):
    queryset = DiscountRule.objects.all()
    serializer_class = DiscountRuleSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DiscountRuleCreateSerializer
        return DiscountRuleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        valid_from = self.request.query_params.get('valid_from')
        valid_until = self.request.query_params.get('valid_until')
        if valid_from:
            qs = qs.filter(valid_from__gte=valid_from)
        if valid_until:
            qs = qs.filter(valid_until__lte=valid_until)
        return qs


class DiscountRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiscountRule.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return DiscountRuleCreateSerializer
        return DiscountRuleSerializer


class DiscountRuleToggleActiveView(generics.UpdateAPIView):
    queryset = DiscountRule.objects.all()
    serializer_class = DiscountRuleSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        return Response(DiscountRuleSerializer(instance).data, status=status.HTTP_200_OK)

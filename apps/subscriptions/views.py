from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MembershipPlan, MembershipAddon, Subscription, SubscriptionTransaction
from .serializers import (
    MembershipPlanSerializer,
    MembershipPlanCreateSerializer,
    MembershipAddonSerializer,
    MembershipAddonCreateSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    SubscriptionTransactionSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


class MembershipPlanListCreateView(generics.ListCreateAPIView):
    queryset = MembershipPlan.objects.all()
    filterset_fields = ['is_active']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MembershipPlanCreateSerializer
        return MembershipPlanSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class MembershipPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MembershipPlan.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return MembershipPlanCreateSerializer
        return MembershipPlanSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class MembershipAddonListCreateView(generics.ListCreateAPIView):
    queryset = MembershipAddon.objects.all()
    filterset_fields = ['is_active', 'plan']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MembershipAddonCreateSerializer
        return MembershipAddonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class MembershipAddonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MembershipAddon.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return MembershipAddonCreateSerializer
        return MembershipAddonSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class SubscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Subscription.objects.select_related('user', 'plan').all()
    filterset_fields = ['status', 'plan']
    search_fields = ['user__email', 'user__username']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubscriptionCreateSerializer
        return SubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.select_related('user', 'plan').all()
    serializer_class = SubscriptionSerializer


class MySubscriptionView(generics.GenericAPIView):
    serializer_class = SubscriptionSerializer

    def get(self, request):
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active',
        ).select_related('plan').first()
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        return Response({'detail': 'No active subscription found.'}, status=404)


class SubscriptionTransactionListCreateView(generics.ListCreateAPIView):
    queryset = SubscriptionTransaction.objects.select_related('subscription').all()
    serializer_class = SubscriptionTransactionSerializer
    filterset_fields = ['status', 'subscription']
    search_fields = ['transaction_id']


class SubscriptionTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionTransaction.objects.select_related('subscription').all()
    serializer_class = SubscriptionTransactionSerializer

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Campaign
from .serializers import (
    CampaignListSerializer,
    CampaignDetailSerializer,
    CampaignCreateSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


@extend_schema(tags=['Marketing Campaigns'])
class CampaignListCreateView(generics.ListCreateAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CampaignCreateSerializer
        return CampaignListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        campaign_type = self.request.query_params.get('type')
        status = self.request.query_params.get('status')
        if campaign_type:
            qs = qs.filter(type=campaign_type)
        if status:
            qs = qs.filter(status=status)
        return qs


@extend_schema(tags=['Marketing Campaigns'])
class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Marketing Campaigns'])
class CampaignArchiveView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def patch(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
        except Campaign.DoesNotExist:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)
        campaign.status = 'archived'
        campaign.save(update_fields=['status'])
        return Response({'detail': 'Campaign archived successfully.'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Marketing Campaigns'])
class CampaignSendView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def post(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
        except Campaign.DoesNotExist:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=['status', 'sent_at'])
        return Response({'detail': 'Campaign sent successfully.'}, status=status.HTTP_200_OK)

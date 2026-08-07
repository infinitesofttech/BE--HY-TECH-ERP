from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import (
    AssetRegistration,
    AssetAssignment,
    AssetDepreciation,
    AssetMaintenance,
    AssetDisposal,
)
from .serializers import (
    AssetRegistrationSerializer,
    AssetAssignmentSerializer,
    AssetDepreciationSerializer,
    AssetMaintenanceSerializer,
    AssetDisposalSerializer,
    AssetAnalyticsSerializer,
)


class AssetRegistrationListCreateView(generics.ListCreateAPIView):
    queryset = AssetRegistration.objects.select_related('asset_user').all()
    serializer_class = AssetRegistrationSerializer
    permission_classes = [IsAuthenticated]


class AssetRegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetRegistration.objects.select_related('asset_user').all()
    serializer_class = AssetRegistrationSerializer
    permission_classes = [IsAuthenticated]


class AssetAssignmentListCreateView(generics.ListCreateAPIView):
    queryset = AssetAssignment.objects.select_related('asset', 'assigned_to').all()
    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]


class AssetAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetAssignment.objects.select_related('asset', 'assigned_to').all()
    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]


class AssetDepreciationListCreateView(generics.ListCreateAPIView):
    queryset = AssetDepreciation.objects.select_related('asset').all()
    serializer_class = AssetDepreciationSerializer
    permission_classes = [IsAuthenticated]


class AssetDepreciationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetDepreciation.objects.select_related('asset').all()
    serializer_class = AssetDepreciationSerializer
    permission_classes = [IsAuthenticated]


class AssetMaintenanceListCreateView(generics.ListCreateAPIView):
    queryset = AssetMaintenance.objects.select_related('asset').all()
    serializer_class = AssetMaintenanceSerializer
    permission_classes = [IsAuthenticated]


class AssetMaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetMaintenance.objects.select_related('asset').all()
    serializer_class = AssetMaintenanceSerializer
    permission_classes = [IsAuthenticated]


class AssetDisposalListCreateView(generics.ListCreateAPIView):
    queryset = AssetDisposal.objects.select_related('asset', 'approved_by').all()
    serializer_class = AssetDisposalSerializer
    permission_classes = [IsAuthenticated]


class AssetDisposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetDisposal.objects.select_related('asset', 'approved_by').all()
    serializer_class = AssetDisposalSerializer
    permission_classes = [IsAuthenticated]


class AssetAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: AssetAnalyticsSerializer(many=True)})
    def get(self, request):
        assets = AssetRegistration.objects.select_related('asset_user').prefetch_related(
            'assignments', 'depreciations', 'maintenances',
        ).all()

        data = []
        for asset in assets:
            depreciation = asset.depreciations.order_by('-created_at').first()
            assignment = asset.assignments.filter(status='active').order_by('-created_at').first()
            open_maintenance = asset.maintenances.filter(
                status__in=['scheduled', 'pending'],
            ).exists()

            if depreciation:
                status = depreciation.status
            elif asset.status == 'inactive':
                status = 'inactive'
            else:
                status = 'active'

            if open_maintenance:
                status = 'maintenance'

            data.append({
                'id': asset.id,
                'asset_name': asset.asset_name,
                'category': asset.category,
                'purchase_cost': depreciation.purchase_cost if depreciation else 0,
                'current_value': depreciation.net_book_value if depreciation else 0,
                'depreciation': depreciation.accumulated_depreciation if depreciation else 0,
                'location': asset.location,
                'assigned_to': assignment.assigned_to.get_full_name() if assignment and assignment.assigned_to else '',
                'status': status,
            })

        return Response(data)

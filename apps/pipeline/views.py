from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import (
    PipelineStage, Pipeline, Lead, Deal, DealActivity, Opportunity, Activity,
)
from .serializers import (
    PipelineStageSerializer, PipelineSerializer, LeadSerializer, DealSerializer,
    DealActivitySerializer, OpportunitySerializer, ActivitySerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


class PipelineStageListCreateView(generics.ListCreateAPIView):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PipelineStageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class LeadListCreateView(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'owner', 'lead_type', 'visibility']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'value']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class DealListCreateView(generics.ListCreateAPIView):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['progress', 'status', 'owner', 'pipeline_stage']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'value', 'expected_close_date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class DealDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class DealActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = DealActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DealActivity.objects.filter(deal_id=self.kwargs['deal_pk'])

    def perform_create(self, serializer):
        serializer.save(deal_id=self.kwargs['deal_pk'], created_by=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class DealActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DealActivity.objects.all()
    serializer_class = DealActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class DealPipelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stages = PipelineStage.objects.all()
        data = []
        for stage in stages:
            deals = Deal.objects.filter(pipeline_stage=stage).select_related('owner')
            data.append({
                'stage_id': stage.id,
                'stage_name': stage.name,
                'probability_default': stage.probability_default,
                'deals': DealSerializer(deals, many=True).data,
            })
        return Response(data)


class PipelineListCreateView(generics.ListCreateAPIView):
    queryset = Pipeline.objects.prefetch_related('stages', 'deals').all()
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PipelineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pipeline.objects.prefetch_related('stages', 'deals').all()
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class OpportunityListCreateView(generics.ListCreateAPIView):
    queryset = Opportunity.objects.select_related('owner').all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'status', 'owner']
    search_fields = ['name', 'account', 'opportunity_id']
    ordering_fields = ['name', 'created_at', 'expected_value', 'expected_close_date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Opportunity.objects.select_related('owner').all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ActivityListCreateView(generics.ListCreateAPIView):
    queryset = Activity.objects.prefetch_related(
        'guests', 'deals', 'contacts', 'companies',
    ).all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activity_type', 'owner']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activity.objects.prefetch_related(
        'guests', 'deals', 'contacts', 'companies',
    ).all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

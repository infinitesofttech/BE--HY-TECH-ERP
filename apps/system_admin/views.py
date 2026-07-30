import sys
import platform

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone

from .models import BackupLog, CronJob, BannedIP, ConnectedApp
from .serializers import (
    BackupLogSerializer,
    BackupLogCreateSerializer,
    CronJobSerializer,
    CronJobCreateSerializer,
    BannedIPSerializer,
    BannedIPCreateSerializer,
    ConnectedAppSerializer,
    ConnectedAppCreateSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove, IsSuperAdmin


class BackupLogListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    queryset = BackupLog.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BackupLogCreateSerializer
        return BackupLogSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BackupLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    queryset = BackupLog.objects.all()
    serializer_class = BackupLogSerializer


class BackupNowView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        log = BackupLog.objects.create(
            filename=f'manual_backup_{timezone.localtime().strftime("%Y%m%d_%H%M%S")}.sql',
            backup_type='full',
            status='completed',
            completed_at=timezone.now(),
            notes='Manual backup triggered via API.',
            created_by=request.user,
        )
        return Response(BackupLogSerializer(log).data, status=status.HTTP_201_CREATED)


class CronJobListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = CronJob.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CronJobCreateSerializer
        return CronJobSerializer


class CronJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = CronJob.objects.all()
    serializer_class = CronJobSerializer


class CronJobToggleActiveView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, pk):
        try:
            cron = CronJob.objects.get(pk=pk)
        except CronJob.DoesNotExist:
            return Response({'error': 'Cron job not found'}, status=status.HTTP_404_NOT_FOUND)
        cron.is_active = not cron.is_active
        cron.save()
        return Response(CronJobSerializer(cron).data)


class BannedIPListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = BannedIP.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BannedIPCreateSerializer
        return BannedIPSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('ip_address', '')
        if search:
            qs = qs.filter(ip_address__icontains=search)
        return qs

    def perform_create(self, serializer):
        serializer.save(banned_by=self.request.user)


class BannedIPDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = BannedIP.objects.all()
    serializer_class = BannedIPSerializer


class ConnectedAppListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = ConnectedApp.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConnectedAppCreateSerializer
        return ConnectedAppSerializer


class ConnectedAppDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = ConnectedApp.objects.all()
    serializer_class = ConnectedAppSerializer


class SystemInfoView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        try:
            import django
            django_version = django.get_version()
        except ImportError:
            django_version = 'unknown'

        db_engine = settings.DATABASES.get('default', {}).get('ENGINE', 'unknown')

        info = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'django_version': django_version,
            'db_engine': db_engine,
            'debug_mode': settings.DEBUG,
            'timezone': settings.TIME_ZONE,
            'media_root': str(settings.MEDIA_ROOT),
            'static_root': str(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else '',
        }
        return Response(info)


class ClearCacheView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        from django.core.cache import cache
        cache.clear()
        return Response({'detail': 'Cache cleared successfully.'}, status=status.HTTP_200_OK)

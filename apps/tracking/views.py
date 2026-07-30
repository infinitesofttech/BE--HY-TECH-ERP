import math
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.accounts.permissions import IsSuperAdmin, IsManagerOrAbove, IsMSR
from .models import TrackingLocation
from .serializers import (
    TrackingLocationSerializer,
    LocationUpdateSerializer,
    LiveLocationSerializer,
)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


class LocationUpdateView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    @extend_schema(request=LocationUpdateSerializer, responses={201: TrackingLocationSerializer})
    def post(self, request):
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        location = TrackingLocation.objects.create(
            employee=request.user,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data.get('speed'),
            address=data.get('address', ''),
            battery_level=data.get('battery_level'),
            timestamp=data.get('timestamp') or timezone.now(),
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'tracking_live',
            {
                'type': 'location_update',
                'data': {
                    'employee_id': location.employee_id,
                    'employee_name': location.employee.get_full_name() or location.employee.email,
                    'latitude': str(location.latitude),
                    'longitude': str(location.longitude),
                    'speed': str(location.speed) if location.speed else None,
                    'address': location.address,
                    'battery_level': location.battery_level,
                    'timestamp': location.timestamp.isoformat(),
                },
            },
        )

        return Response(
            TrackingLocationSerializer(location).data,
            status=status.HTTP_201_CREATED,
        )


class LiveLocationsView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    def get(self, request):
        latest_subquery = Subquery(
            TrackingLocation.objects.filter(employee=OuterRef('employee'))
            .order_by('-timestamp')
            .values('id')[:1]
        )
        latest_locations = TrackingLocation.objects.filter(
            id__in=latest_subquery
        ).select_related('employee')

        results = []
        for loc in latest_locations:
            employee = loc.employee
            name = getattr(employee, 'full_name', None) or employee.email
            results.append({
                'employee_id': employee.id,
                'employee_name': name,
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'speed': loc.speed,
                'last_updated': loc.timestamp,
                'battery_level': loc.battery_level,
            })

        serializer = LiveLocationSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RouteHistoryView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    def get(self, request, employee_id):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'detail': 'Query parameter "date" is required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
        end = start + timezone.timedelta(days=1)

        locations = TrackingLocation.objects.filter(
            employee_id=employee_id,
            timestamp__gte=start,
            timestamp__lt=end,
        ).order_by('timestamp')

        serializer = TrackingLocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DailyDistanceView(APIView):
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    def get(self, request, employee_id):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'detail': 'Query parameter "date" is required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
        end = start + timezone.timedelta(days=1)

        locations = TrackingLocation.objects.filter(
            employee_id=employee_id,
            timestamp__gte=start,
            timestamp__lt=end,
        ).order_by('timestamp')

        total_distance = 0.0
        count = locations.count()

        if count < 2:
            return Response({
                'total_distance_km': 0.0,
                'total_points': count,
                'first_location_time': locations.first().timestamp if count == 1 else None,
                'last_location_time': locations.last().timestamp if count == 1 else None,
            }, status=status.HTTP_200_OK)

        points = list(locations)
        for i in range(1, len(points)):
            total_distance += haversine(
                float(points[i - 1].latitude),
                float(points[i - 1].longitude),
                float(points[i].latitude),
                float(points[i].longitude),
            )

        return Response({
            'total_distance_km': round(total_distance, 2),
            'total_points': count,
            'first_location_time': points[0].timestamp,
            'last_location_time': points[-1].timestamp,
        }, status=status.HTTP_200_OK)


class TrackingHistoryView(generics.ListAPIView):
    serializer_class = TrackingLocationSerializer
    permission_classes = [IsSuperAdmin | IsManagerOrAbove | IsMSR]

    def get_queryset(self):
        qs = TrackingLocation.objects.select_related('employee').all()

        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)

        return qs

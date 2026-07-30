from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date

from .models import CalendarEvent, Holiday
from .serializers import (
    CalendarEventSerializer,
    CalendarEventCreateSerializer,
    HolidaySerializer,
    HolidayCreateSerializer,
)


class CalendarEventListCreateView(generics.ListCreateAPIView):
    queryset = CalendarEvent.objects.select_related('created_by').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CalendarEventCreateSerializer
        return CalendarEventSerializer

    def get_queryset(self):
        qs = self.queryset
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        event_type = self.request.query_params.get('event_type')

        if date_from:
            qs = qs.filter(start_datetime__gte=date_from)
        if date_to:
            qs = qs.filter(end_datetime__lte=date_to)
        if event_type:
            qs = qs.filter(event_type=event_type)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = CalendarEventSerializer(serializer.instance, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class CalendarEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CalendarEvent.objects.select_related('created_by').all()
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class HolidayListCreateView(generics.ListCreateAPIView):
    queryset = Holiday.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HolidayCreateSerializer
        return HolidaySerializer

    def get_queryset(self):
        qs = self.queryset
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')

        if year:
            qs = qs.filter(date__year=year)
        if month:
            qs = qs.filter(date__month=month)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = HolidaySerializer(serializer.instance, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class HolidayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class UpcomingHolidaysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        holidays = Holiday.objects.filter(
            date__gte=today, is_active=True
        ).order_by('date')[:10]
        serializer = HolidaySerializer(holidays, many=True, context={'request': request})
        return Response(serializer.data)

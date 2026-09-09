from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import Reminder, FollowUp, PendingWork, Application
from .serializers import (
    ReminderSerializer, FollowUpSerializer,
    PendingWorkSerializer, ApplicationSerializer
)


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all().select_related('customer', 'service').prefetch_related('follow_ups')
    serializer_class = ReminderSerializer
    permission_classes = [AllowAny]
    lookup_field = 'reminder_no'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'service', 'priority', 'follow_up_status', 'reminder_type']
    search_fields = ['reminder_no', 'subject', 'customer__head_of_family', 'customer__mobile_number', 'customer__family_id']
    ordering_fields = ['due_date', 'reminder_date', 'created_at', 'priority']
    ordering = ['-created_at']

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        val = self.kwargs.get(self.lookup_field)
        try:
            if str(val).isdigit():
                return queryset.get(Q(reminder_no=val) | Q(id=int(val)))
            return queryset.get(reminder_no=val)
        except Reminder.DoesNotExist:
            return get_object_or_404(queryset, Q(reminder_no__iexact=val))

    @action(detail=True, methods=['get', 'post'], url_path='follow-ups')
    def follow_ups(self, request, reminder_no=None):
        reminder = self.get_object()
        if request.method == 'GET':
            qs = reminder.follow_ups.all().order_by('-created_at')
            return Response(FollowUpSerializer(qs, many=True).data)
        
        data = request.data.copy()
        data['reminder'] = reminder.id
        serializer = FollowUpSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reminder=reminder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'patch', 'delete'], url_path=r'follow-ups/(?P<follow_up_id>[^/.]+)')
    def follow_up_detail(self, request, reminder_no=None, follow_up_id=None):
        reminder = self.get_object()
        follow_up = get_object_or_404(FollowUp, reminder=reminder, id=follow_up_id)
        if request.method == 'DELETE':
            follow_up.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = FollowUpSerializer(follow_up, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PendingWorkViewSet(viewsets.ModelViewSet):
    queryset = PendingWork.objects.all().select_related('customer', 'service', 'assigned_staff')
    serializer_class = PendingWorkSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pending_no'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'service', 'priority', 'work_status', 'assigned_staff']
    search_fields = ['pending_no', 'customer__head_of_family', 'customer__mobile_number', 'customer__family_id', 'pending_reason', 'next_action']
    ordering_fields = ['expected_date', 'pending_since', 'created_at', 'priority']
    ordering = ['-created_at']

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        val = self.kwargs.get(self.lookup_field)
        try:
            if str(val).isdigit():
                return queryset.get(Q(pending_no=val) | Q(id=int(val)))
            return queryset.get(pending_no=val)
        except PendingWork.DoesNotExist:
            return get_object_or_404(queryset, Q(pending_no__iexact=val))

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        now = timezone.now().date()
        qs = self.get_queryset()
        total = qs.count()
        pending = qs.filter(work_status='PENDING').count()
        in_progress = qs.filter(work_status='IN_PROGRESS').count()
        blocked = qs.filter(work_status='BLOCKED').count()
        completed = qs.filter(work_status='COMPLETED').count()
        high_priority = qs.filter(priority='HIGH').exclude(work_status='COMPLETED').count()
        overdue = qs.filter(expected_date__lt=now).exclude(work_status='COMPLETED').count()

        return Response({
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'blocked': blocked,
            'completed': completed,
            'high_priority': high_priority,
            'overdue': overdue,
        })


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all().select_related('customer', 'family_member', 'service', 'sub_service', 'assigned_staff')
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'application_no'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'service', 'sub_service', 'category', 'status', 'priority', 'payment_status']
    search_fields = ['application_no', 'applicant_name', 'applicant_mobile', 'customer__head_of_family', 'customer__mobile_number', 'government_app_no']
    ordering_fields = ['created_at', 'expected_date', 'priority', 'status']
    ordering = ['-created_at']

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        val = self.kwargs.get(self.lookup_field)
        try:
            if str(val).isdigit():
                return queryset.get(Q(application_no=val) | Q(id=int(val)))
            return queryset.get(application_no=val)
        except Application.DoesNotExist:
            return get_object_or_404(queryset, Q(application_no__iexact=val))

    @action(detail=True, methods=['patch', 'put'], url_path='status')
    def update_status(self, request, application_no=None):
        app = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        if new_status:
            old_status = app.status
            app.status = new_status
            timeline_list = list(app.timeline or [])
            timeline_list.append({
                'id': len(timeline_list) + 1,
                'timestamp': timezone.now().isoformat(),
                'actor_name': request.user.get_full_name() if request.user.is_authenticated else 'Staff Officer',
                'actor_role': 'STAFF',
                'action': f"Status changed from {old_status} to {new_status}",
                'old_status': old_status,
                'new_status': new_status,
                'notes': notes
            })
            app.timeline = timeline_list
            app.save(update_fields=['status', 'timeline', 'updated_at'])
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, application_no=None):
        app = self.get_object()
        return Response(app.timeline or [])

from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.accounts.permissions import IsManagerOrAbove
from .models import Notification, NotificationRecipient
from .serializers import (
    NotificationSerializer,
    NotificationDetailSerializer,
    SendNotificationSerializer,
    NotificationRecipientSerializer,
)

User = get_user_model()


class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    @extend_schema(request=SendNotificationSerializer, responses={201: NotificationSerializer})
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        recipient_type = data['recipient_type']

        notification = Notification.objects.create(
            title=data['title'],
            message=data['message'],
            attachment=data.get('attachment'),
            sent_by=request.user,
            recipient_type=recipient_type,
        )

        recipients_qs = User.objects.filter(is_active=True)

        if recipient_type == 'all':
            pass
        elif recipient_type == 'selected':
            recipients_qs = recipients_qs.filter(pk__in=data['recipient_ids'])
        elif recipient_type == 'pin_code':
            recipients_qs = recipients_qs.filter(pin_code=data['recipient_pin_code'])
        elif recipient_type == 'territory':
            recipients_qs = recipients_qs.filter(territory=data['recipient_territory'])

        recipients = list(recipients_qs)
        if recipients:
            NotificationRecipient.objects.bulk_create([
                NotificationRecipient(
                    notification=notification,
                    recipient=r,
                )
                for r in recipients
            ])
            from .push import send_push_to_user
            for r in recipients:
                push_data = {'notification_id': str(notification.id), 'type': 'notification'}
                send_push_to_user(r, data['title'], data['message'], data=push_data)

        output = NotificationSerializer(notification)
        return Response(output.data, status=status.HTTP_201_CREATED)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        notifications = Notification.objects.filter(
            recipients__recipient=user,
        ).select_related('sent_by').distinct()

        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() in ('true', '1'):
                notifications = notifications.filter(recipients__is_read=True)
            elif is_read.lower() in ('false', '0'):
                notifications = notifications.filter(recipients__is_read=False)

        return notifications


class AllSentNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get_queryset(self):
        return Notification.objects.select_related('sent_by').all()


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.select_related('sent_by').all()


class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipient, created = NotificationRecipient.objects.get_or_create(
            notification=notification,
            recipient=request.user,
        )

        if not recipient.is_read:
            recipient.is_read = True
            recipient.read_at = timezone.now()
            recipient.save()

        return Response({'status': 'marked as read'})


class MarkAllAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        updated = NotificationRecipient.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

        return Response({'marked_count': updated})


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = NotificationRecipient.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

        return Response({'unread_count': count})

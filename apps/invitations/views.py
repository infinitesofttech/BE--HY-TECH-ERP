import uuid
from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsManagerOrAbove

from .models import Invitation
from .serializers import InvitationCreateSerializer, InvitationSerializer


class InvitationListCreateView(generics.ListCreateAPIView):
    queryset = Invitation.objects.all()
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'email']
    search_fields = ['email', 'role']
    ordering_fields = ['created_at', 'sent_at', 'expires_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvitationCreateSerializer
        return InvitationSerializer

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)


class InvitationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]


class InvitationAcceptView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'password': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'phone': {'type': 'string'},
            },
            'required': ['password'],
        },
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
    )
    def post(self, request, token):
        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            return Response({'error': 'Invalid invitation token.'}, status=status.HTTP_404_NOT_FOUND)

        if invitation.status != 'pending':
            return Response(
                {'error': f'Invitation is already {invitation.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.expires_at < timezone.now():
            invitation.status = 'expired'
            invitation.save()
            return Response({'error': 'Invitation has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=invitation.email).exists():
            return Response(
                {'error': 'A user with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            username=invitation.email,
            email=invitation.email,
            password=password,
            role=invitation.role,
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
            phone=request.data.get('phone', ''),
        )

        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.save()

        return Response({'message': 'Invitation accepted successfully.'}, status=status.HTTP_200_OK)


class InvitationResendView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    @extend_schema(
        request=None,
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
    )
    def post(self, request, pk):
        try:
            invitation = Invitation.objects.get(pk=pk)
        except Invitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        if invitation.status == 'accepted':
            return Response(
                {'error': 'Cannot resend an accepted invitation.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.token = uuid.uuid4()
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.status = 'pending'
        invitation.sent_at = timezone.now()
        invitation.save()

        return Response({'message': 'Invitation resent successfully.'}, status=status.HTTP_200_OK)

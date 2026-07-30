from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import User, ContactInfo, Feedback, TwoFactorCode, EmailVerification, DeleteAccountRequest
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserCreateSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    ContactInfoSerializer,
    FeedbackSerializer,
    TwoFactorVerifySerializer,
    TwoFactorEnableSerializer,
    EmailVerificationRequestSerializer,
    EmailVerificationConfirmSerializer,
    DeleteAccountRequestSerializer,
)
from .permissions import IsSuperAdmin, IsManagerOrAbove, IsOwnerOrManagerOrAdmin


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [IsSuperAdmin]

    @extend_schema(request=UserCreateSerializer, responses={201: UserSerializer})
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrAdmin]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProfileUpdateSerializer, responses={200: UserSerializer})
    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


class EmployeeListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'territory', 'pin_code', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['date_joined', 'first_name', 'last_name']

    def get_queryset(self):
        return User.objects.select_related('manager').all()


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related('manager').all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAbove]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class EmployeeToggleActiveView(APIView):
    permission_classes = [IsManagerOrAbove]

    @extend_schema(responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}, 'is_active': {'type': 'boolean'}}}})
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Employee not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        if not user.is_active:
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)

        return Response({
            'detail': f'Employee {"activated" if user.is_active else "deactivated"} successfully.',
            'is_active': user.is_active,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={205: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}},
    )
    def post(self, request):
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)


class RegisterDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={'type': 'object', 'properties': {'device_token': {'type': 'string'}}},
        responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}},
    )
    def post(self, request):
        token = request.data.get('device_token')
        if not token:
            return Response({'detail': 'device_token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.device_token = token
        request.user.save(update_fields=['device_token'])
        return Response({'detail': 'Device token registered successfully.'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={'type': 'object', 'properties': {'email': {'type': 'string'}}},
        responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}, 'reset_token': {'type': 'string'}}}},
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'If this email exists, a reset link will be sent.'}, status=status.HTTP_200_OK)

        from django.utils.crypto import get_random_string
        reset_token = get_random_string(64)
        user.set_password(reset_token)
        user.save(update_fields=['password'])

        return Response({
            'detail': 'Password has been reset. Check your email for the new temporary password.',
            'reset_token': reset_token,
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={'type': 'object', 'properties': {
            'email': {'type': 'string'},
            'new_password': {'type': 'string'},
        }},
        responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}},
    )
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        old_password = request.data.get('old_password')

        if not email or not new_password:
            return Response({'detail': 'Email and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if old_password and not user.check_password(old_password):
            return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class DeviceListView(APIView):
    permission_classes = [IsManagerOrAbove]

    @extend_schema(
        responses={200: {'type': 'array', 'items': {'type': 'object', 'properties': {
            'id': {'type': 'integer'}, 'email': {'type': 'string'}, 'device_token': {'type': 'string'},
        }}}},
    )
    def get(self, request):
        users_with_devices = User.objects.filter(
            is_active=True,
        ).exclude(device_token__isnull=True).exclude(device_token='').values(
            'id', 'email', 'device_token',
        )
        return Response(users_with_devices, status=status.HTTP_200_OK)


class ContactInfoView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: ContactInfoSerializer})
    def get(self, request):
        contact = ContactInfo.objects.first()
        if not contact:
            return Response(
                {'detail': 'Contact info not available.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ContactInfoSerializer(contact)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ContactInfoSerializer, responses={201: ContactInfoSerializer})
    def post(self, request):
        if request.user.role not in ['super_admin']:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ContactInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ContactInfoSerializer, responses={200: ContactInfoSerializer})
    def put(self, request):
        if request.user.role not in ['super_admin']:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        contact = ContactInfo.objects.first()
        if not contact:
            return Response({'detail': 'No contact info to update.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactInfoSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]
    queryset = Feedback.objects.all()


class FeedbackListView(generics.ListAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    queryset = Feedback.objects.all()
    ordering = ['-created_at']


class TwoFactorEnableView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=TwoFactorEnableSerializer, responses={201: {'type': 'object', 'properties': {'detail': {'type': 'string'}, 'code': {'type': 'string'}}}})
    def post(self, request):
        from django.utils import timezone
        from django.utils.crypto import get_random_string
        import datetime

        TwoFactorCode.objects.filter(user=request.user, is_used=False).update(is_used=True)

        code = get_random_string(6, allowed_chars='0123456789')
        expires_at = timezone.now() + datetime.timedelta(minutes=5)

        TwoFactorCode.objects.create(
            user=request.user,
            code=code,
            expires_at=expires_at,
        )

        return Response({
            'detail': '2FA code generated successfully.',
            'code': code,
        }, status=status.HTTP_201_CREATED)


class TwoFactorVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=TwoFactorVerifySerializer, responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}})
    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        from django.utils import timezone
        try:
            two_factor = TwoFactorCode.objects.filter(
                user=request.user,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now(),
            ).latest('created_at')
        except TwoFactorCode.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        two_factor.is_used = True
        two_factor.save(update_fields=['is_used'])

        return Response({'detail': 'Code verified successfully.'}, status=status.HTTP_200_OK)


class EmailVerificationRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=EmailVerificationRequestSerializer, responses={201: {'type': 'object', 'properties': {'detail': {'type': 'string'}, 'token': {'type': 'string'}}}})
    def post(self, request):
        serializer = EmailVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        from django.utils import timezone
        from django.utils.crypto import get_random_string
        import datetime

        token = get_random_string(64)

        EmailVerification.objects.create(
            user=request.user,
            token=token,
            email=email,
            expires_at=timezone.now() + datetime.timedelta(hours=24),
        )

        return Response({
            'detail': 'Verification email sent.',
            'token': token,
        }, status=status.HTTP_201_CREATED)


class EmailVerificationConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=EmailVerificationConfirmSerializer, responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}})
    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        from django.utils import timezone

        try:
            verification = EmailVerification.objects.get(token=token, verified_at__isnull=True, expires_at__gt=timezone.now())
        except EmailVerification.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification.verified_at = timezone.now()
        verification.save(update_fields=['verified_at'])

        return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)


class DeleteAccountRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=DeleteAccountRequestSerializer, responses={201: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}})
    def post(self, request):
        serializer = DeleteAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        DeleteAccountRequest.objects.create(
            user=request.user,
            reason=serializer.validated_data['reason'],
        )

        return Response({'detail': 'Delete account request submitted.'}, status=status.HTTP_201_CREATED)

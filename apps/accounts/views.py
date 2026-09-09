from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from apps.contacts.serializers import CompanySerializer
from .models import (
    User, ContactInfo, Feedback, DeleteAccountRequest, LoginLog, Role, UserActivityLog,
    DesignDocument,
)
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserCreateSerializer,
    CompanyRegisterSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    ContactInfoSerializer,
    FeedbackSerializer,
    DeleteAccountRequestSerializer,
    RoleSerializer,
    LoginLogSerializer,
    UserActivityLogSerializer,
    DesignDocumentSerializer,
    DesignDocumentCreateSerializer,
)
from .permissions import (
    IsSuperAdmin, IsManagerOrAbove, IsOwnerOrManagerOrAdmin, IsCompany, IsDesigner,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        ip_address = self._client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        LoginLog.objects.create(
            user=user, status='success', ip_address=ip_address, device=user_agent,
        )

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)

    @staticmethod
    def _client_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


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


class CompanyRegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=CompanyRegisterSerializer,
        responses={201: CompanyRegisterSerializer},
    )
    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return Response({
            'detail': 'Company registered successfully.',
            'company_id': company.id,
            'company_name': company.name,
            'email': company.email,
        }, status=status.HTTP_201_CREATED)


class CompanyProfileView(APIView):
    permission_classes = [IsCompany]

    @extend_schema(responses={200: {'type': 'object'}})
    def get(self, request):
        from apps.contacts.models import Company
        from apps.contacts.serializers import CompanySerializer
        company = Company.objects.filter(owner=request.user).first()
        if not company:
            return Response(
                {'detail': 'No company profile found for this account.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CompanySerializer(company).data, status=status.HTTP_200_OK)

    @extend_schema(request=CompanySerializer, responses={200: {'type': 'object'}})
    def patch(self, request):
        from apps.contacts.models import Company
        from apps.contacts.serializers import CompanySerializer
        company = Company.objects.filter(owner=request.user).first()
        if not company:
            return Response(
                {'detail': 'No company profile found for this account.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyDashboardView(APIView):
    permission_classes = [IsCompany]

    @extend_schema(responses={200: {'type': 'object'}})
    def get(self, request):
        from apps.contacts.models import Company
        from apps.pipeline.models import Lead, Deal
        from apps.projects.models import Project, Task
        from apps.contacts.models import Contact
        from apps.invoices.models import Invoice
        from django.db.models import Sum, Count, Q

        company = Company.objects.filter(owner=request.user).first()
        if not company:
            return Response(
                {'detail': 'No company profile found for this account.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        leads = Lead.objects.filter(
            Q(company=company) | Q(contacts__company=company)
        ).distinct()
        deals = Deal.objects.filter(
            Q(company=company)
            | Q(related_companies=company)
            | Q(contact__company=company)
        ).distinct()
        projects = Project.objects.filter(
            Q(company=company)
            | Q(deals__company=company)
        ).distinct()
        contacts = Contact.objects.filter(
            Q(company=company) | Q(companies_list=company)
        ).distinct()
        tasks = Task.objects.filter(
            Q(project__company=company)
            | Q(project__deals__company=company)
        ).distinct()
        invoices = Invoice.objects.filter(company=company)

        total_deals_value = deals.aggregate(
            total=Sum('value'),
        )['total'] or 0

        won_deals = deals.filter(status='won').count()
        open_deals = deals.filter(status='open').count()

        return Response({
            'company': {
                'id': company.id,
                'name': company.name,
                'email': company.email,
                'phone': company.phone,
                'website': company.website,
                'industry': company.industry.name if company.industry else None,
            },
            'summary': {
                'total_leads': leads.count(),
                'won_leads': leads.filter(status='won').count(),
                'lost_leads': leads.filter(status='lost').count(),
                'total_deals': deals.count(),
                'open_deals': open_deals,
                'won_deals': won_deals,
                'total_deals_value': total_deals_value,
                'total_projects': projects.count(),
                'active_projects': projects.filter(status='active').count(),
                'inactive_projects': projects.filter(status='inactive').count(),
                'total_tasks': tasks.count(),
                'active_tasks': tasks.filter(status='active').count(),
                'inactive_tasks': tasks.filter(status='inactive').count(),
                'total_contacts': contacts.count(),
                'total_invoices': invoices.count(),
                'paid_invoices': invoices.filter(status='paid').count(),
            },
        }, status=status.HTTP_200_OK)


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
        return User.objects.select_related(
            'manager', 'department', 'designation',
        ).all()


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related(
        'manager', 'department', 'designation',
    ).all()
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

        log = LoginLog.objects.filter(
            user=request.user, status='success', logout_time__isnull=True,
        ).first()
        if log:
            from django.utils import timezone
            log.logout_time = timezone.now()
            duration = (log.logout_time - log.login_time).total_seconds()
            log.session_duration = max(int(duration), 0)
            log.save()

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
        from django.core.mail import send_mail
        from django.conf import settings

        reset_token = get_random_string(64)
        user.set_password(reset_token)
        user.save(update_fields=['password'])

        send_mail(
            subject='Your temporary password',
            message=f'Your account password has been reset.\n\nTemporary password: {reset_token}\n\nPlease log in and change your password immediately.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({
            'detail': 'Password has been reset. Check your email for the new temporary password.',
        }, status=status.HTTP_200_OK)


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


class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class LoginLogListView(generics.ListAPIView):
    queryset = LoginLog.objects.select_related('user').all()
    serializer_class = LoginLogSerializer
    permission_classes = [IsManagerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'device']
    ordering_fields = ['login_time', 'logout_time']


class UserActivityLogListCreateView(generics.ListCreateAPIView):
    queryset = UserActivityLog.objects.select_related('user').all()
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'module', 'action']
    search_fields = ['user__email', 'action', 'module', 'record_id']
    ordering_fields = ['action_date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DesignDocumentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'is_public']
    search_fields = ['design_no', 'title', 'description', 'designer__email']
    ordering_fields = ['created_at', 'updated_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DesignDocumentCreateSerializer
        return DesignDocumentSerializer

    def get_queryset(self):
        queryset = DesignDocument.objects.select_related(
            'designer',
        ).prefetch_related('visible_to').all()
        user = self.request.user
        if user.role in ['super_admin', 'manager', 'designer']:
            return queryset
        if user.department_id is not None:
            queryset = queryset.filter(
                Q(is_public=True)
                | Q(visible_to=user.department_id)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        return queryset

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsDesigner()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        visible_to = data.get('visible_to')
        if visible_to is not None and isinstance(visible_to, str):
            value = visible_to.strip()
            if value.startswith('['):
                import json
                try:
                    parsed = json.loads(value)
                    visible_to = parsed if isinstance(parsed, list) else [parsed]
                except ValueError:
                    visible_to = []
            else:
                visible_to = [
                    int(p) for p in value.split(',') if p.strip()
                ]
            data.setlist('visible_to', visible_to)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        design = serializer.save(designer=request.user)
        return Response(
            DesignDocumentSerializer(design).data,
            status=status.HTTP_201_CREATED,
        )


class DesignDocumentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DesignDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['super_admin', 'manager', 'designer']:
            return DesignDocument.objects.select_related(
                'designer',
            ).prefetch_related('visible_to').all()
        if self.request.user.department_id is not None:
            return DesignDocument.objects.select_related(
                'designer',
            ).prefetch_related('visible_to').filter(
                Q(is_public=True)
                | Q(visible_to=self.request.user.department_id)
            ).distinct()
        return DesignDocument.objects.select_related(
            'designer',
        ).prefetch_related('visible_to').filter(is_public=True)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsDesigner()]
        return [IsAuthenticated()]

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Notification
from .serializers import EmployeeUserSerializer, NotificationSerializer
from apps.hytech_customers.models import Customer, ServiceVisit, VisitDocument
from apps.hytech_services.models import Transaction
from apps.hytech_operations.models import PendingWork, Reminder, Application

User = get_user_model()

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class StaffLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("🔥 STAFF LOGIN VIEW REACHED")
        username_or_email = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username_or_email or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate
        user = authenticate(username=username_or_email, password=password)
        if not user:
            # Try by email
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj and user_obj.check_password(password):
                user = user_obj

        if not user:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'User account is inactive.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        user_type = 'admin' if (user.is_superuser or user.role in ['admin', 'hr']) else 'employee'

        return Response({
            'message': 'Staff login successful.',
            'user_type': user_type,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'employee': EmployeeUserSerializer(user).data
        })


class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('mobile_number') or request.data.get('family_id') or request.data.get('username')
        if not identifier:
            return Response({'error': 'Mobile number or Family ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        identifier = str(identifier).strip()
        customer = Customer.objects.filter(
            Q(mobile_number=identifier) | Q(family_id__iexact=identifier)
        ).first()

        if not customer:
            return Response({'error': 'Customer household not found with this mobile or Family ID.'}, status=status.HTTP_404_NOT_FOUND)

        # Find or create a user representation for JWT
        user, _ = User.objects.get_or_create(
            username=f"cust_{customer.family_id.lower().replace('-', '_')}",
            defaults={
                'email': f"{customer.family_id.lower()}@hytech.local",
                'role': 'customer',
                'first_name': customer.head_of_family,
                'phone': customer.mobile_number
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Customer login successful.',
            'user_type': 'customer',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'customer': {
                'id': customer.id,
                'family_id': customer.family_id,
                'head_of_family': customer.head_of_family,
                'mobile_number': customer.mobile_number,
                'current_points': customer.current_points,
                'wallet_balance': str(customer.wallet_balance),
                'village_city': customer.village_city
            }
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).order_by('-id')
    serializer_class = EmployeeUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username') or data.get('email', '').split('@')[0]
        email = data.get('email', '')
        password = data.get('password') or 'Hytech@123'
        role = str(data.get('role', 'staff')).lower()
        if role not in ['admin', 'staff', 'hr', 'customer']:
            role = 'staff'

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=data.get('full_name', '').split(' ')[0],
            last_name=' '.join(data.get('full_name', '').split(' ')[1:]) if ' ' in data.get('full_name', '') else '',
            phone=data.get('mobile_number') or data.get('phone', ''),
            role=role,
            is_staff=(role in ['admin', 'staff', 'hr'])
        )
        return Response(EmployeeUserSerializer(user).data, status=status.HTTP_201_CREATED)


class DashboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        today = timezone.now().date()

        # Today's summary
        total_customers = Customer.objects.count()
        today_service_entries = ServiceVisit.objects.filter(visit_date=today).count()
        if today_service_entries == 0:
            today_service_entries = ServiceVisit.objects.count()

        open_pending_work = PendingWork.objects.exclude(work_status='COMPLETED').count()
        ready_for_delivery = Application.objects.filter(status__in=['APPROVED', 'COMPLETED']).count()
        pending_reminders = Reminder.objects.filter(follow_up_status='PENDING').count()

        # Business summary
        txn_aggregates = Transaction.objects.aggregate(
            total_billing=Sum('bill_amount'),
            advance_received=Sum('paid_amount'),
            outstanding_balance=Sum('due_amount')
        )
        total_billing = float(txn_aggregates['total_billing'] or 0)
        advance_received = float(txn_aggregates['advance_received'] or 0)
        outstanding_balance = float(txn_aggregates['outstanding_balance'] or 0)

        completed_services = ServiceVisit.objects.filter(status='COMPLETED').count()
        delivered_services = Application.objects.filter(status='COMPLETED').count()

        # Customer summary
        active_members = Customer.objects.filter(is_active=True).count()
        vip_members = Customer.objects.filter(current_points__gte=30).count()
        repeat_customers = Customer.objects.filter(total_visits__gt=1).count()
        urgent_tasks = PendingWork.objects.filter(priority='HIGH').exclude(work_status='COMPLETED').count()
        documents_pending = VisitDocument.objects.filter(status='NOT_AVAILABLE').count()

        return Response({
            'today_summary': {
                'total_customers': total_customers,
                'total_service_entries': today_service_entries,
                'open_pending_work': open_pending_work,
                'ready_for_delivery': ready_for_delivery,
                'pending_reminders': pending_reminders,
            },
            'business_summary': {
                'total_billing': total_billing,
                'advance_received': advance_received,
                'outstanding_balance': outstanding_balance,
                'completed_services': completed_services,
                'delivered_services': delivered_services,
            },
            'customer_summary': {
                'active_members': active_members,
                'vip_members': vip_members,
                'repeat_customers': repeat_customers,
                'urgent_tasks': urgent_tasks,
                'documents_pending': documents_pending,
            }
        })


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # /notifications/send/
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['patch', 'put'], url_path='read')
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notif).data)

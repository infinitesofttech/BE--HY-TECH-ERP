from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Customer, FamilyMember, CustomerDocument, ServiceVisit, VisitDocument
from .serializers import (
    CustomerSerializer, FamilyMemberSerializer,
    CustomerDocumentSerializer, ServiceVisitSerializer,
    VisitDocumentSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
    lookup_field = 'family_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['family_id', 'head_of_family', 'mobile_number', 'village_city', 'whatsapp_number']
    ordering_fields = ['created_at', 'head_of_family', 'registration_date', 'total_visits']
    ordering = ['-created_at']

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        val = self.kwargs[lookup_url_kwarg]

        # Try lookup by family_id first, then numeric id
        try:
            if str(val).isdigit():
                return queryset.get(Q(family_id=val) | Q(id=int(val)))
            return queryset.get(family_id=val)
        except Customer.DoesNotExist:
            return get_object_or_404(queryset, Q(family_id__iexact=val) | Q(id__iexact=val) if str(val).isdigit() else Q(family_id__iexact=val))


class FamilyMemberViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyMemberSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        family_id = self.kwargs.get('family_id')
        qs = FamilyMember.objects.all()
        if family_id:
            if str(family_id).isdigit():
                qs = qs.filter(Q(family_id=family_id) | Q(customer__id=int(family_id)))
            else:
                qs = qs.filter(family_id__iexact=family_id)
        return qs

    def perform_create(self, serializer):
        family_id = self.kwargs.get('family_id')

        customer = Customer.objects.filter(
            family_id__iexact=family_id
        ).first()

        if not customer:
            raise serializers.ValidationError({
                'family_id': 'Customer family not found.'
            })

        serializer.save(
            customer=customer,
            family_id=customer.family_id
        )

        customer.family_member_count = customer.members.count()
        customer.save(update_fields=['family_member_count'])


class CustomerDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerDocumentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        family_id = self.kwargs.get('family_id')
        member_id = self.kwargs.get('member_id')

        qs = CustomerDocument.objects.all()

        if family_id:
            if str(family_id).isdigit():
                qs = qs.filter(
                    Q(family_id=family_id) |
                    Q(customer__id=int(family_id))
                )
            else:
                qs = qs.filter(
                    family_id__iexact=family_id
                )

        if member_id and str(member_id).lower() != 'all' and str(member_id) != '0':
            qs = qs.filter(
                family_member_id=member_id
            )

        return qs

    def create(self, request, *args, **kwargs):

        family_id = self.kwargs.get('family_id')
        member_id = self.kwargs.get('member_id')

        # -------------------------
        # Find Customer
        # -------------------------

        customer = None

        if family_id:
            if str(family_id).isdigit():
                customer = Customer.objects.filter(
                    Q(family_id=family_id) |
                    Q(id=int(family_id))
                ).first()
            else:
                customer = Customer.objects.filter(
                    family_id__iexact=family_id
                ).first()

        if not customer:
            return Response(
                {
                    'family_id': 'Customer family not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------
        # Find Family Member
        # -------------------------

        member = None

        if member_id and str(member_id).isdigit() and int(member_id) > 0:

            member = FamilyMember.objects.filter(
                id=int(member_id),
                customer=customer
            ).first()

            if not member:
                return Response(
                    {
                        'member_id': 'Family member not found in this family.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        # -------------------------
        # Validate request body
        # -------------------------

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # -------------------------
        # Save
        # -------------------------

        serializer.save(
            customer=customer,
            family_id=customer.family_id,
            family_member=member,
            member_name=member.name if member else ''
        )

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class ServiceVisitViewSet(viewsets.ModelViewSet):
    queryset = ServiceVisit.objects.all().select_related('customer', 'family_member', 'service', 'sub_service', 'checked_by').prefetch_related('documents')
    serializer_class = ServiceVisitSerializer
    permission_classes = [AllowAny]
    lookup_field = 'visit_no'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['visit_no', 'customer__head_of_family', 'customer__mobile_number', 'customer__family_id', 'service__ServiceName', 'sub_service__SubServiceName']
    ordering_fields = ['visit_date', 'created_at', 'status']
    ordering = ['-created_at']

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        val = self.kwargs.get(self.lookup_field)
        try:
            if str(val).isdigit():
                return queryset.get(Q(visit_no=val) | Q(id=int(val)))
            return queryset.get(visit_no=val)
        except ServiceVisit.DoesNotExist:
            return get_object_or_404(queryset, Q(visit_no__iexact=val))

    @action(detail=True, methods=['patch', 'put'], url_path=r'documents/(?P<doc_id>[^/.]+)')
    def update_document(self, request, visit_no=None, doc_id=None):
        visit = self.get_object()
        doc = get_object_or_404(VisitDocument, visit=visit, id=doc_id)

        file_obj = request.FILES.get('document_file') or request.FILES.get('file')
        if file_obj:
            doc.document_file = file_obj
            doc.status = 'AVAILABLE'
        if 'status' in request.data:
            doc.status = request.data['status']
        if 'document_name' in request.data:
            doc.document_name = request.data['document_name']
        doc.save()

        # Also sync to Customer digital vault
        if file_obj and visit.customer:
            CustomerDocument.objects.update_or_create(
                customer=visit.customer,
                family_member=visit.family_member,
                document_type=doc.document_type,
                defaults={
                    'document_name': doc.document_name,
                    'document_file': doc.document_file,
                    'is_verified': True,
                    'family_id': visit.customer.family_id,
                    'member_name': visit.family_member.name if visit.family_member else visit.customer.head_of_family
                }
            )

        return Response(VisitDocumentSerializer(doc).data, status=status.HTTP_200_OK)

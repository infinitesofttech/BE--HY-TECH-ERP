from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date

from .models import Village, ContactInquiry, AuditLog
from .serializers import VillageSerializer, ContactInquirySerializer, AuditLogSerializer
from apps.hytech_customers.models import Customer, FamilyMember, CustomerDocument


class VillageViewSet(viewsets.ModelViewSet):
    queryset = Village.objects.all()
    serializer_class = VillageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'code'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['taluka', 'district', 'is_active']
    search_fields = ['code', 'name', 'name_gu', 'taluka', 'district']
    ordering_fields = ['name', 'total_families', 'total_citizens']
    ordering = ['id']

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        val = self.kwargs.get(self.lookup_field)
        if str(val).isdigit():
            return queryset.filter(id=int(val)).first() or get_object_or_404(queryset, code__iexact=val)
        return get_object_or_404(queryset, code__iexact=val)

    @action(detail=False, methods=['get'], url_path=r'(?P<code>[^/]+)/family-tree/(?P<family_id>[^/]+)')
    def family_tree_by_village(self, request, code=None, family_id=None):
        return self._build_family_tree(family_id)

    @action(detail=False, methods=['get'], url_path=r'family-tree/(?P<family_id>[^/]+)')
    def family_tree(self, request, family_id=None):
        return self._build_family_tree(family_id)

    def _build_family_tree(self, family_id):
        customer = Customer.objects.filter(family_id__iexact=family_id).first()
        if not customer:
            # Fallback to first customer
            customer = Customer.objects.first()
        
        if not customer:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        members = list(customer.members.all())
        today = date.today()

        def calc_age(bdate):
            if not bdate:
                return 40
            return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))

        def get_member_docs(member):
            docs = CustomerDocument.objects.filter(customer=customer, family_member=member)
            doc_items = []
            for d in docs:
                doc_items.append({
                    'id': str(d.id),
                    'title': d.document_name,
                    'title_gu': d.get_document_type_display(),
                    'type': d.document_type,
                    'status': 'VERIFIED' if d.is_verified else ('UPLOADED' if d.document_file else 'MISSING'),
                    'document_no': f"DOC-{d.id:04d}",
                    'uploaded_date': d.created_at.strftime('%d %b %Y'),
                    'file_url': d.document_file.url if d.document_file else None,
                    'is_required': True
                })
            return doc_items

        head_member = next((m for m in members if m.relationship == 'HEAD'), None)
        if not head_member:
            head_member = members[0] if members else None

        spouse_member = next((m for m in members if m.relationship in ['WIFE', 'HUSBAND']), None)
        children_members = [m for m in members if m.relationship in ['SON', 'DAUGHTER']]
        other_members = [m for m in members if m != head_member and m != spouse_member and m not in children_members]

        def member_to_node(m, is_head=False, gen=2):
            docs = get_member_docs(m)
            verified_count = sum(1 for d in docs if d['status'] == 'VERIFIED')
            return {
                'id': m.id,
                'family_id': customer.family_id,
                'name': m.name,
                'relationship': m.relationship,
                'relationship_display': m.get_relationship_display(),
                'gender': m.gender,
                'age': calc_age(m.birth_date),
                'birth_date': str(m.birth_date or '1980-01-01'),
                'mobile_number': m.mobile_number or customer.mobile_number,
                'is_head': is_head,
                'is_active': m.is_active,
                'generation': gen,
                'documents_verified': verified_count,
                'documents_total': max(len(docs), 1),
                'documents': docs,
                'children': []
            }

        head_node = member_to_node(head_member, is_head=True, gen=2) if head_member else {
            'id': 1,
            'family_id': customer.family_id,
            'name': customer.head_of_family,
            'relationship': 'HEAD',
            'relationship_display': 'Head of Family',
            'gender': 'MALE',
            'age': 45,
            'birth_date': str(customer.birth_date or '1980-01-01'),
            'mobile_number': customer.mobile_number,
            'is_head': True,
            'is_active': True,
            'generation': 2,
            'documents_verified': 1,
            'documents_total': 1,
            'documents': [],
            'children': []
        }

        spouse_node = member_to_node(spouse_member, is_head=False, gen=2) if spouse_member else None
        children_nodes = [member_to_node(c, is_head=False, gen=3) for c in children_members]

        # Add other relatives to children or as appropriate
        for o in other_members:
            gen = 1 if o.relationship in ['FATHER', 'MOTHER'] else 3
            children_nodes.append(member_to_node(o, is_head=False, gen=gen))

        return Response({
            'head': head_node,
            'spouse': spouse_node,
            'children': children_nodes
        })


class ContactInquiryViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all()
    serializer_class = ContactInquirySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['full_name', 'mobile_number', 'email', 'subject', 'message']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_role', 'action', 'entity_type']
    search_fields = ['user_name', 'action', 'entity_id', 'details', 'ip_address']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

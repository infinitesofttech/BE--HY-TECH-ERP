from rest_framework import serializers
from .models import Customer, FamilyMember, CustomerDocument, ServiceVisit, VisitDocument


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            'id', 'customer', 'family_id', 'name', 'relationship',
            'gender', 'mobile_number', 'birth_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'customer', 'family_id', 'created_at']


class CustomerDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = CustomerDocument
        fields = [
            'id', 'customer', 'family_member', 'family_id', 'member_name',
            'document_type', 'document_type_display', 'document_name',
            'document_file', 'description', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'family_id', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    members = FamilyMemberSerializer(many=True, read_only=True)
    documents = CustomerDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'family_id', 'registration_date', 'head_of_family',
            'mobile_number', 'whatsapp_number', 'family_member_count',
            'village_city', 'birth_date', 'referral_family_id',
            'document_consent', 'current_points', 'wallet_balance',
            'total_visits', 'last_visit', 'is_active', 'notes',
            'digital_card_sent', 'created_at', 'updated_at',
            'members', 'documents'
        ]
        read_only_fields = ['id',  'family_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        customer = super().create(validated_data)
        # Automatically create head member
        FamilyMember.objects.create(
            customer=customer,
            name=customer.head_of_family,
            relationship='HEAD',
            mobile_number=customer.mobile_number,
            birth_date=customer.birth_date,
            is_active=True
        )
        return customer


class VisitDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitDocument
        fields = [
            'id', 'document_type', 'document_name', 'status',
            'document_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceVisitSerializer(serializers.ModelSerializer):
    customer_family_id = serializers.CharField(source='customer.family_id', read_only=True)
    customer_name = serializers.CharField(source='customer.head_of_family', read_only=True)
    customer_mobile = serializers.CharField(source='customer.mobile_number', read_only=True)
    family_member_name = serializers.CharField(source='family_member.name', read_only=True, default='')
    service_name = serializers.CharField(source='service.ServiceName', read_only=True, default='')
    sub_service_name = serializers.CharField(source='sub_service.SubServiceName', read_only=True, default='')
    checked_by_name = serializers.SerializerMethodField()
    documents = VisitDocumentSerializer(many=True, read_only=True)
    total_documents = serializers.SerializerMethodField()
    available_documents = serializers.SerializerMethodField()

    class Meta:
        model = ServiceVisit
        fields = [
            'id', 'visit_no', 'customer', 'customer_family_id', 'customer_name',
            'customer_mobile', 'family_member', 'family_member_name',
            'service', 'service_name', 'sub_service', 'sub_service_name',
            'checked_by', 'checked_by_name', 'status', 'visit_date', 'remarks',
            'documents', 'total_documents', 'available_documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'visit_no', 'created_at', 'updated_at']

    def get_checked_by_name(self, obj):
        if obj.checked_by:
            return obj.checked_by.get_full_name() or obj.checked_by.username
        return "Staff Officer"

    def get_total_documents(self, obj):
        return obj.documents.count()

    def get_available_documents(self, obj):
        return obj.documents.filter(status='AVAILABLE').count()

    def create(self, validated_data):
        visit = super().create(validated_data)
        # Update customer visit count
        customer = visit.customer
        customer.total_visits += 1
        customer.last_visit = visit.visit_date
        customer.save(update_fields=['total_visits', 'last_visit'])

        # Auto-inspect vault against sub-service required documents
        sub_service = visit.sub_service
        if sub_service:
            # Query required documents for this sub_service
            req_docs = sub_service.required_documents.all()
            for req in req_docs:
                # Check customer vault
                vault_match = CustomerDocument.objects.filter(
                    customer=customer,
                    document_type=req.document_type
                ).first()
                if visit.family_member:
                    member_match = CustomerDocument.objects.filter(
                        customer=customer,
                        family_member=visit.family_member,
                        document_type=req.document_type
                    ).first()
                    if member_match:
                        vault_match = member_match

                status = 'AVAILABLE' if (vault_match and vault_match.document_file) else 'NOT_AVAILABLE'
                doc_file = vault_match.document_file if vault_match else None
                VisitDocument.objects.create(
                    visit=visit,
                    document_type=req.document_type,
                    document_name=req.DocumentName,
                    status=status,
                    document_file=doc_file
                )
        return visit

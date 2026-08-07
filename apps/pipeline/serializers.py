from rest_framework import serializers
from django.db.models import Sum

from .models import (
    PipelineStage, Pipeline, Lead, Deal, DealActivity, Opportunity, Activity,
)


class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = '__all__'


class PipelineSerializer(serializers.ModelSerializer):
    total_deal_value = serializers.SerializerMethodField()
    deals_count = serializers.SerializerMethodField()

    class Meta:
        model = Pipeline
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_deal_value(self, obj):
        total = obj.deals.aggregate(total=Sum('value'))['total']
        return float(total or 0)

    def get_deals_count(self, obj):
        return obj.deals.count()


class DealActivitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True, default='')

    class Meta:
        model = DealActivity
        fields = '__all__'


class LeadSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.email', read_only=True, default='')
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'name', 'lead_type', 'company_name',
            'email', 'phone', 'status', 'value', 'product_requirement',
            'quantity', 'owner', 'owner_name', 'source', 'industry', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DealSerializer(serializers.ModelSerializer):
    activities = DealActivitySerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    pipeline_name = serializers.SerializerMethodField()
    progress_name = serializers.SerializerMethodField()

    class Meta:
        model = Deal
        fields = '__all__'

    def get_owner_name(self, obj):
        return obj.owner.email if obj.owner else ''

    def get_lead_name(self, obj):
        return obj.lead.name if obj.lead else ''

    def get_contact_name(self, obj):
        return str(obj.contact) if obj.contact else ''

    def get_company_name(self, obj):
        return str(obj.company) if obj.company else ''

    def get_pipeline_name(self, obj):
        return obj.pipeline.name if obj.pipeline else ''

    def get_progress_name(self, obj):
        return obj.get_progress_display() if obj.progress else ''


class OpportunitySerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    stage_name = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['id', 'opportunity_id', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.email if obj.owner else ''

    def get_stage_name(self, obj):
        return obj.get_stage_display() if obj.stage else ''


class ActivitySerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    deal_names = serializers.SerializerMethodField()
    contact_names = serializers.SerializerMethodField()
    company_names = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.email if obj.owner else ''

    def get_deal_names(self, obj):
        return [d.name for d in obj.deals.all()]

    def get_contact_names(self, obj):
        return [str(c) for c in obj.contacts.all()]

    def get_company_names(self, obj):
        return [c.name for c in obj.companies.all()]

    def get_created_by_name(self, obj):
        return obj.created_by.email if obj.created_by else ''

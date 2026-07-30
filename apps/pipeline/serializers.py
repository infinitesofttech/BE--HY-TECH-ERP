from rest_framework import serializers
from .models import PipelineStage, Lead, Deal, DealActivity


class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = '__all__'


class DealActivitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True, default='')

    class Meta:
        model = DealActivity
        fields = '__all__'


class LeadSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.email', read_only=True, default='')

    class Meta:
        model = Lead
        fields = '__all__'


class DealSerializer(serializers.ModelSerializer):
    activities = DealActivitySerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    stage_name = serializers.SerializerMethodField()

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

    def get_stage_name(self, obj):
        return obj.get_stage_display() if obj.stage else ''

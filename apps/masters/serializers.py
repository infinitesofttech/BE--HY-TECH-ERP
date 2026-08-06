from rest_framework import serializers
from .models import (
    Dealer, Retailer, Currency, Source, Industry,
    ContactStage, LostReason, CallReason, CallLog,
)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'


class DealerSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.email', read_only=True, default='')

    class Meta:
        model = Dealer
        fields = '__all__'


class RetailerSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.email', read_only=True, default='')

    class Meta:
        model = Retailer
        fields = '__all__'


class ContactStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactStage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class LostReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostReason
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CallReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallReason
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CallLogSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True, default='')

    class Meta:
        model = CallLog
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at']

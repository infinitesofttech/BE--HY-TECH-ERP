from rest_framework import serializers
from .models import Dealer, Retailer, Mechanic, TaxRate, Currency, Source, Industry


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'


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


class MechanicSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.email', read_only=True, default='')

    class Meta:
        model = Mechanic
        fields = '__all__'

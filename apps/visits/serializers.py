from rest_framework import serializers
from .models import Visit


class VisitSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source='employee.email', read_only=True,
    )
    dealer_name = serializers.CharField(
        source='dealer.name', read_only=True, default='',
    )
    retailer_name = serializers.CharField(
        source='retailer.name', read_only=True, default='',
    )

    class Meta:
        model = Visit
        fields = '__all__'
        read_only_fields = ['employee', 'created_at']


class VisitCheckInSerializer(serializers.Serializer):
    visit_type = serializers.ChoiceField(choices=Visit.VISIT_TYPE_CHOICES)
    dealer_id = serializers.IntegerField(required=False)
    retailer_id = serializers.IntegerField(required=False)
    purpose = serializers.CharField(required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    photo = serializers.ImageField(required=False)
    check_in_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    check_in_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    check_in_address = serializers.CharField(
        max_length=500, required=False, allow_blank=True,
    )

    def validate(self, attrs):
        visit_type = attrs['visit_type']
        if visit_type == 'dealer' and not attrs.get('dealer_id'):
            raise serializers.ValidationError(
                {'dealer_id': 'dealer_id is required for dealer visits.'},
            )
        if visit_type == 'retailer' and not attrs.get('retailer_id'):
            raise serializers.ValidationError(
                {'retailer_id': 'retailer_id is required for retailer visits.'},
            )
        return attrs


class VisitCheckOutSerializer(serializers.Serializer):
    check_out_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    check_out_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    check_out_address = serializers.CharField(
        max_length=500, required=False, allow_blank=True,
    )
    remarks = serializers.CharField(required=False, allow_blank=True)

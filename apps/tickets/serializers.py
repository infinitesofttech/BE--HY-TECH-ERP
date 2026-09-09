from rest_framework import serializers
from .models import Ticket, TicketReply


class TicketReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketReply
        fields = '__all__'
        read_only_fields = ['ticket']


class TicketSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_customer_name(self, obj):
        if obj.customer is None:
            return ''
        return obj.customer.email

    def get_assigned_to_name(self, obj):
        if obj.assigned_to is None:
            return ''
        return obj.assigned_to.email

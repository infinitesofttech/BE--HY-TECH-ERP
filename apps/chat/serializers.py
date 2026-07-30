from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_sender_name(self, obj):
        return obj.sender.email

    def get_receiver_name(self, obj):
        return obj.receiver.email


class ConversationSerializer(serializers.ModelSerializer):
    participant_names = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = '__all__'

    def get_participant_names(self, obj):
        return [p.email for p in obj.participants.all()]

    def get_last_message_preview(self, obj):
        return obj.last_message[:50] if obj.last_message else ''

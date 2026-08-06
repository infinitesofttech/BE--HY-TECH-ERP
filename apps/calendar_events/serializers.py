from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CalendarEvent, Holiday

User = get_user_model()


class CalendarEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    attendee_ids = serializers.SerializerMethodField()
    attendee_names = serializers.SerializerMethodField()

    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'description', 'event_type',
            'start_datetime', 'end_datetime', 'is_all_day',
            'location', 'color', 'created_by', 'created_by_name',
            'created_by_email', 'attendees', 'attendee_ids',
            'attendee_names', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_attendee_ids(self, obj):
        return list(obj.attendees.values_list('id', flat=True))

    def get_attendee_names(self, obj):
        return [
            f'{u.get_full_name() or u.email}'
            for u in obj.attendees.all()
        ]


class CalendarEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'event_type',
            'start_datetime', 'end_datetime', 'is_all_day',
            'location', 'color', 'attendees',
        ]

    def validate(self, attrs):
        if attrs['end_datetime'] <= attrs['start_datetime']:
            raise serializers.ValidationError('End date/time must be after start date/time.')
        return attrs

    def create(self, validated_data):
        attendees = validated_data.pop('attendees', [])
        validated_data['created_by'] = self.context['request'].user
        event = CalendarEvent.objects.create(**validated_data)
        if attendees:
            event.attendees.set(attendees)
        return event


class HolidaySerializer(serializers.ModelSerializer):
    holiday_status = serializers.SerializerMethodField()

    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'description', 'type', 'holiday_status',
            'is_recurring_yearly', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_holiday_status(self, obj):
        from datetime import date, timedelta
        today = date.today()
        if obj.date < today:
            return 'past'
        if obj.date == today:
            return 'today'
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        if obj.date <= end_of_week:
            return 'this_week'
        return 'upcoming'


class HolidayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'description', 'type', 'is_recurring_yearly']

from rest_framework import serializers
from .models import (
    Project, Task, TodoItem, Timesheet, Milestone, ResourceAllocation,
)


class ProjectSerializer(serializers.ModelSerializer):
    team_leader_name = serializers.SerializerMethodField()
    responsible_person_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_team_leader_name(self, obj):
        if obj.team_leader:
            return obj.team_leader.get_full_name() or obj.team_leader.email
        return ''

    def get_responsible_person_names(self, obj):
        return [
            u.get_full_name() or u.email
            for u in obj.responsible_persons.all()
        ]


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    assignee_names = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_project_name(self, obj):
        return obj.project.name if obj.project else ''

    def get_assignee_names(self, obj):
        return [
            u.get_full_name() or u.email
            for u in obj.assignees.all()
        ]


class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = '__all__'
        read_only_fields = ['user']


class TimesheetSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    task_name = serializers.SerializerMethodField()

    class Meta:
        model = Timesheet
        fields = '__all__'

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return ''

    def get_project_name(self, obj):
        return obj.project.name if obj.project else ''

    def get_task_name(self, obj):
        return obj.task.title if obj.task else ''


class MilestoneSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Milestone
        fields = '__all__'

    def get_project_name(self, obj):
        return obj.project.name if obj.project else ''

    def get_owner_name(self, obj):
        if obj.owner:
            return obj.owner.get_full_name() or obj.owner.email
        return ''


class ResourceAllocationSerializer(serializers.ModelSerializer):
    resource_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = ResourceAllocation
        fields = '__all__'

    def get_resource_name(self, obj):
        return obj.resource.get_full_name() or obj.resource.email

    def get_project_name(self, obj):
        return obj.project.name if obj.project else ''


class ProjectAnalyticsSerializer(serializers.Serializer):
    project = serializers.CharField()
    project_id = serializers.IntegerField()
    lead = serializers.CharField()
    progress = serializers.FloatField()
    budget = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    spent = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    health = serializers.CharField()

from rest_framework import serializers
from .models import Project, Task, TodoItem, Timesheet


class ProjectSerializer(serializers.ModelSerializer):
    team_leader_name = serializers.SerializerMethodField()
    responsible_person_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_team_leader_name(self, obj):
        return obj.team_leader.email if obj.team_leader else ''

    def get_responsible_person_names(self, obj):
        return [u.email for u in obj.responsible_persons.all()]


class TaskSerializer(serializers.ModelSerializer):
    assignee_names = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_assignee_names(self, obj):
        return [u.email for u in obj.assignees.all()]


class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = '__all__'
        read_only_fields = ['user']


class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = '__all__'

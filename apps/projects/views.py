from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import (
    Project, Task, TodoItem, Timesheet, Milestone, ResourceAllocation,
)
from .serializers import (
    ProjectSerializer,
    TaskSerializer,
    TodoItemSerializer,
    TimesheetSerializer,
    MilestoneSerializer,
    ResourceAllocationSerializer,
    ProjectAnalyticsSerializer,
)
from apps.accounts.permissions import IsManagerOrAbove


@extend_schema(tags=['Projects'])
class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'client_name']
    search_fields = ['name', 'client_name', 'project_id', 'description']
    ordering_fields = ['name', 'created_at', 'start_date', 'due_date', 'budget']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Projects'])
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Tasks'])
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.select_related('project').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'category', 'priority', 'status', 'is_important']
    search_fields = ['title', 'description', 'tags', 'project__name']
    ordering_fields = ['title', 'created_at', 'start_date', 'due_date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Tasks'])
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.select_related('project').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Todos'])
class TodoItemListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return TodoItem.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Todos'])
class TodoItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TodoItem.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Timesheets'])
class TimesheetListCreateView(generics.ListCreateAPIView):
    queryset = Timesheet.objects.select_related('user', 'project', 'task').all()
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'project', 'task', 'date']
    ordering_fields = ['date', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Timesheets'])
class TimesheetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Timesheet.objects.select_related('user', 'project', 'task').all()
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Milestones'])
class MilestoneListCreateView(generics.ListCreateAPIView):
    queryset = Milestone.objects.select_related('project', 'owner').all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'owner', 'status']
    search_fields = ['name', 'milestone_id', 'notes']
    ordering_fields = ['name', 'created_at', 'date', 'progress']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Milestones'])
class MilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Milestone.objects.select_related('project', 'owner').all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Resource Allocations'])
class ResourceAllocationListCreateView(generics.ListCreateAPIView):
    queryset = ResourceAllocation.objects.select_related('resource', 'project').all()
    serializer_class = ResourceAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource', 'project', 'role']
    search_fields = ['role', 'project__name', 'resource__email']
    ordering_fields = ['created_at', 'hours', 'allocated', 'availability']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


@extend_schema(tags=['Resource Allocations'])
class ResourceAllocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResourceAllocation.objects.select_related('resource', 'project').all()
    serializer_class = ResourceAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


def _project_health(project, progress, budget, spent):
    today = timezone.localdate()
    if progress >= 100 or project.status == 'inactive':
        return 'completed'
    utilization = float(spent / budget) if budget else 0
    if utilization >= 1.0:
        return 'critical'
    if project.due_date and project.due_date < today:
        return 'critical'
    if utilization >= 0.85:
        return 'risk'
    if progress >= 50:
        return 'on_track'
    return 'healthy'


@extend_schema(tags=['Project Analytics'])
class ProjectAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Project.objects.prefetch_related('deals__lead', 'milestones').all()
        project_id = request.query_params.get('project')
        if project_id:
            qs = qs.filter(id=project_id)

        data = []
        for project in qs:
            lead = next(
                (d.lead for d in project.deals.all() if d.lead), None
            )
            milestones = project.milestones.all()
            progress = 0
            if milestones:
                progress = sum(m.progress for m in milestones) / len(milestones)
            spent = Timesheet.objects.filter(project=project).aggregate(
                total=Sum('used_hours')
            )['total'] or 0
            budget = project.budget or 0
            data.append({
                'project_id': project.id,
                'project': project.name,
                'lead': lead.name if lead else '',
                'progress': round(progress, 2),
                'budget': project.budget,
                'spent': spent,
                'health': _project_health(project, progress, budget, spent),
            })

        serializer = ProjectAnalyticsSerializer(data, many=True)
        return Response(serializer.data)

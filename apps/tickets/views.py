from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Ticket, TicketReply
from .serializers import TicketSerializer, TicketReplySerializer


@extend_schema(tags=['Tickets'])
class TicketListCreateView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'customer']
    search_fields = ['subject', 'description', 'ticket_id']
    ordering_fields = ['created_at', 'updated_at', 'priority']


@extend_schema(tags=['Tickets'])
class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=['Tickets'])
class TicketReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketReplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TicketReply.objects.filter(ticket_id=self.kwargs['ticket_pk'])

    def perform_create(self, serializer):
        serializer.save(ticket_id=self.kwargs['ticket_pk'], user=self.request.user)


@extend_schema(tags=['Tickets'])
class TicketReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketReplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TicketReply.objects.filter(ticket_id=self.kwargs['ticket_pk'])

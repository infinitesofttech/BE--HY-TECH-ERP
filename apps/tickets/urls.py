from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.TicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:ticket_pk>/replies/', views.TicketReplyListCreateView.as_view(), name='ticket-reply-list'),
    path('tickets/<int:ticket_pk>/replies/<int:pk>/', views.TicketReplyDetailView.as_view(), name='ticket-reply-detail'),
]

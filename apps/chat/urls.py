from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_pk>/messages/', views.MessageListCreateView.as_view(), name='message-list'),
    path('conversations/<int:conversation_pk>/messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('unread-count/', views.UnreadCountView.as_view(), name='chat-unread-count'),
]

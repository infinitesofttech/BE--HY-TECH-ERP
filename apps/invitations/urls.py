from django.urls import path

from . import views

urlpatterns = [
    path('', views.InvitationListCreateView.as_view()),
    path('<int:pk>/', views.InvitationDetailView.as_view()),
    path('accept/<str:token>/', views.InvitationAcceptView.as_view()),
    path('<int:pk>/resend/', views.InvitationResendView.as_view()),
]

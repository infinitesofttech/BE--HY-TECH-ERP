from django.urls import path
from . import views

urlpatterns = [
    path('check-in/', views.VisitCheckInView.as_view(), name='visit-check-in'),
    path('check-out/', views.VisitCheckOutView.as_view(), name='visit-check-out'),
    path('', views.VisitListView.as_view(), name='visit-list'),
    path('<int:pk>/', views.VisitDetailView.as_view(), name='visit-detail'),
    path('today/', views.TodayVisitsView.as_view(), name='visit-today'),
    path('report/', views.VisitReportView.as_view(), name='visit-report'),
    path('export/', views.VisitExportView.as_view(), name='visit-export'),
]

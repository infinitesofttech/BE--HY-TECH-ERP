from django.urls import path
from . import views

urlpatterns = [
    path('location/', views.LocationUpdateView.as_view(), name='location-update'),
    path('live/', views.LiveLocationsView.as_view(), name='live-locations'),
    path('route/<int:employee_id>/', views.RouteHistoryView.as_view(), name='route-history'),
    path('distance/<int:employee_id>/', views.DailyDistanceView.as_view(), name='daily-distance'),
    path('history/', views.TrackingHistoryView.as_view(), name='tracking-history'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.CalendarEventListCreateView.as_view()),
    path('events/<int:pk>/', views.CalendarEventDetailView.as_view()),
    path('holidays/', views.HolidayListCreateView.as_view()),
    path('holidays/<int:pk>/', views.HolidayDetailView.as_view()),
    path('holidays/upcoming/', views.UpcomingHolidaysView.as_view()),
]

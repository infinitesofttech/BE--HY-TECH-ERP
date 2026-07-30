from django.contrib import admin
from .models import TrackingLocation


@admin.register(TrackingLocation)
class TrackingLocationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'latitude', 'longitude', 'speed', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('employee__email', 'address')
    list_per_page = 25

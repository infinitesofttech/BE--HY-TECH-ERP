from django.contrib import admin
from .models import AttendanceType, Attendance


@admin.register(AttendanceType)
class AttendanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'punch_in_time', 'punch_out_time', 'total_hours', 'overtime')
    list_filter = ('status', 'date')
    search_fields = ('employee__email', 'employee__first_name')
    list_per_page = 25

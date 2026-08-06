from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ContactInfo, Feedback, Role, LoginLog, UserActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = [
        'email', 'first_name', 'last_name', 'role', 'territory',
        'is_active', 'is_staff',
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'state', 'city']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone', 'avatar',
                'date_of_birth', 'address', 'city', 'state',
            ),
        }),
        ('Employment', {
            'fields': (
                'role', 'territory', 'pin_code', 'manager', 'joining_date',
            ),
        }),
        ('Device', {
            'fields': ('device_token',),
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'role',
                'phone', 'password1', 'password2',
            ),
        }),
    )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['phone', 'email', 'working_hours']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time', 'session_duration', 'ip_address', 'status']
    list_filter = ['status', 'login_time']
    search_fields = ['user__email', 'device']


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'module', 'record_id', 'ip_address', 'action_date']
    list_filter = ['module', 'action_date']
    search_fields = ['user__email', 'action', 'module']

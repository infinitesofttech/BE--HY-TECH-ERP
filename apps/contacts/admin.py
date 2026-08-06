from django.contrib import admin
from .models import Company, Contact, ContactMessage


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'industry', 'city', 'status', 'owner')
    list_filter = ('status', 'industry', 'city')
    search_fields = ('name', 'email', 'phone', 'industry__name')
    list_per_page = 25


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'email', 'phone', 'company', 'job_title', 'source', 'owner', 'visibility')
    list_filter = ('source', 'company', 'job_title', 'type', 'visibility')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'job_title')
    filter_horizontal = ('visible_to',)
    list_per_page = 25


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)

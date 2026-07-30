from django.contrib import admin
from .models import Company, Contact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'industry', 'city', 'status', 'owner')
    list_filter = ('status', 'industry', 'city')
    search_fields = ('name', 'email', 'phone', 'industry__name')
    list_per_page = 25


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'job_title', 'source', 'owner')
    list_filter = ('source', 'company', 'job_title')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'job_title')
    list_per_page = 25

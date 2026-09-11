from django.contrib import admin
from .models import BaseService, SubService, RequiredDocument, Transaction


@admin.register(BaseService)
class BaseServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'ServiceName', 'Category', 'SubCategory', 'Department',
        'ServiceType', 'GovernmentFee', 'ServiceCharge', 'TotalFee',
        'SlaDays', 'Priority', 'IsOfficial', 'IsActive',
    ]
    list_filter = ['Category', 'ServiceType', 'Priority', 'IsOfficial', 'IsActive']
    search_fields = ['ServiceName', 'ServiceNameGu', 'Department']
    readonly_fields = ['CreatedAt', 'UpdatedAt']


@admin.register(SubService)
class SubServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'SubServiceName', 'Service', 'IsActive', 'CreatedAt',
    ]
    list_filter = ['IsActive']
    search_fields = ['SubServiceName', 'Service__ServiceName']
    readonly_fields = ['CreatedAt', 'UpdatedAt']


@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'DocumentName', 'SubService', 'document_type', 'IsRequired', 'CreatedAt',
    ]
    list_filter = ['document_type', 'IsRequired']
    search_fields = ['DocumentName', 'SubService__SubServiceName']
    readonly_fields = ['CreatedAt']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'transaction_no', 'transaction_date', 'customer', 'service',
        'staff', 'bill_amount', 'paid_amount', 'due_amount',
        'payment_status', 'payment_mode', 'created_at',
    ]
    list_filter = ['payment_status', 'payment_mode', 'transaction_date']
    search_fields = [
        'transaction_no', 'customer__head_of_family', 'customer__family_id',
        'staff__email',
    ]
    readonly_fields = ['transaction_no', 'created_at', 'updated_at']

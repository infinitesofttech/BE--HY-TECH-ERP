from django.contrib import admin
from .models import Customer, FamilyMember, CustomerDocument, ServiceVisit, VisitDocument


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 0


class CustomerDocumentInline(admin.TabularInline):
    model = CustomerDocument
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('family_id', 'head_of_family', 'mobile_number', 'village_city', 'current_points', 'wallet_balance', 'is_active')
    search_fields = ('family_id', 'head_of_family', 'mobile_number', 'village_city')
    list_filter = ('is_active', 'village_city', 'registration_date')
    inlines = [FamilyMemberInline, CustomerDocumentInline]

    def save_model(self, request, obj, form, change):
        # If raw password entered, hash it
        if obj.password and not obj.password.startswith(('pbkdf2_', 'argon2', 'bcrypt')):
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'family_id', 'relationship', 'gender', 'mobile_number', 'is_active')
    search_fields = ('name', 'family_id', 'mobile_number')
    list_filter = ('relationship', 'gender', 'is_active')


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_name', 'document_type', 'family_id', 'member_name', 'is_verified')
    search_fields = ('document_name', 'family_id', 'member_name')
    list_filter = ('document_type', 'is_verified')


@admin.register(ServiceVisit)
class ServiceVisitAdmin(admin.ModelAdmin):
    list_display = ('visit_no', 'customer', 'service', 'status', 'visit_date')
    search_fields = ('visit_no', 'customer__family_id', 'customer__head_of_family')
    list_filter = ('status', 'visit_date')

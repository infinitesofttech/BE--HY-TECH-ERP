from django.contrib import admin
from .models import EmailTemplate, EmailCampaign, SubscriberList

admin.site.register(EmailTemplate)
admin.site.register(EmailCampaign)


@admin.register(SubscriberList)
class SubscriberListAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_contacts', 'active_subscribers', 'bounce_rate', 'last_campaign_date', 'created_at')
    search_fields = ('name',)

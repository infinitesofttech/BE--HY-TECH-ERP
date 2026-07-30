from django.contrib import admin
from .models import EmailTemplate, EmailCampaign

admin.site.register(EmailTemplate)
admin.site.register(EmailCampaign)

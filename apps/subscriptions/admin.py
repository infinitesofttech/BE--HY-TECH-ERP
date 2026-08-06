from django.contrib import admin
from .models import *

admin.site.register(MembershipPlan)
admin.site.register(MembershipAddon)
admin.site.register(Subscription)
admin.site.register(SubscriptionTransaction)

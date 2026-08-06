from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # App URLs
    path('api/auth/', include('apps.accounts.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/tracking/', include('apps.tracking.urls')),
    path('api/dealers/', include('apps.masters.urls_dealers')),
    path('api/retailers/', include('apps.masters.urls_retailers')),
    path('api/visits/', include('apps.visits.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/purchases/', include('apps.purchases.urls')),
    path('api/production/', include('apps.production.urls')),
    path('api/targets/', include('apps.targets.urls')),
    path('api/leaves/', include('apps.leaves.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/pipeline/', include('apps.pipeline.urls')),
    path('api/contacts/', include('apps.contacts.urls')),
    path('api/invoices/', include('apps.invoices.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/contracts/', include('apps.contracts.urls')),
    path('api/email-marketing/', include('apps.email_marketing.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/blog/', include('apps.blog.urls')),
    path('api/config/', include('apps.masters.urls_config')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/marketing/', include('apps.marketing.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/estimations/', include('apps.estimations.urls')),
    path('api/settings/', include('apps.settings_config.urls')),
    path('api/content/', include('apps.content_management.urls')),
    path('api/system/', include('apps.system_admin.urls')),
    path('api/calendar/', include('apps.calendar_events.urls')),
    path('api/invitations/', include('apps.invitations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

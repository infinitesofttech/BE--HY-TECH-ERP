from django.db import migrations
from django.db.models import Q


def backfill_lead_company(apps, schema_editor):
    Lead = apps.get_model('pipeline', 'Lead')
    Company = apps.get_model('contacts', 'Company')
    for lead in Lead.objects.filter(company__isnull=True).exclude(company_name=''):
        company = Company.objects.filter(
            Q(name__iexact=lead.company_name)
        ).first()
        if company:
            lead.company = company
            lead.save(update_fields=['company'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0007_lead_company'),
    ]

    operations = [
        migrations.RunPython(backfill_lead_company, noop),
    ]

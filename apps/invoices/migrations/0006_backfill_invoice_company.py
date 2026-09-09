from django.db import migrations
from django.db.models import Q


def backfill_invoice_company(apps, schema_editor):
    Invoice = apps.get_model('invoices', 'Invoice')
    Company = apps.get_model('contacts', 'Company')
    for invoice in Invoice.objects.filter(company__isnull=True):
        company = Company.objects.filter(
            Q(name__iexact=invoice.customer_name)
            | Q(email__iexact=invoice.customer_email)
        ).first()
        if company:
            invoice.company = company
            invoice.save(update_fields=['company'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0005_invoice_company'),
    ]

    operations = [
        migrations.RunPython(backfill_invoice_company, noop),
    ]

# Seed finance.Tax from the removed masters.TaxRate records.

from django.db import migrations


def seed_taxes_from_taxrate(apps, schema_editor):
    TaxRate = apps.get_model('masters', 'TaxRate')
    Tax = apps.get_model('finance', 'Tax')

    for tr in TaxRate.objects.all():
        if Tax.objects.filter(rate=tr.rate).exists():
            continue
        Tax.objects.create(
            tax_id=f'TAX-{tr.rate}',
            name=tr.name,
            rate=tr.rate,
            status='active' if tr.is_active else 'inactive',
            applied_to='both',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0002_currency_industry_source_taxrate'),
        ('finance', '0003_budget_cashflow_expense_expensecategory_income_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_taxes_from_taxrate, migrations.RunPython.noop),
    ]

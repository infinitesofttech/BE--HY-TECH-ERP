# Remove masters.TaxRate; tax is now owned by finance.Tax.
# Data was migrated to finance.Tax in finance 0004_seed_tax_from_taxrate.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_seed_tax_from_taxrate'),
        ('masters', '0004_callreason_contactstage_lostreason_calllog'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TaxRate',
        ),
    ]

# Generated manually: ProductCategory now uses name, slug, status(active/inactive).

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    ProductCategory = apps.get_model('products', 'ProductCategory')
    for category in ProductCategory.objects.all():
        if not category.slug:
            category.slug = slugify(category.name)
        category.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_tourplan_end_date_tourplan_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='slug',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='productcategory',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10),
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='description',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='is_active',
        ),
    ]

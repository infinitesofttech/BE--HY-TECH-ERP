from django.db import migrations
from django.db.models import Q


def backfill_project_company(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Company = apps.get_model('contacts', 'Company')
    for project in Project.objects.filter(company__isnull=True).exclude(client_name=''):
        company = Company.objects.filter(
            Q(name__iexact=project.client_name)
        ).first()
        if company:
            project.company = company
            project.save(update_fields=['company'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_company'),
    ]

    operations = [
        migrations.RunPython(backfill_project_company, noop),
    ]

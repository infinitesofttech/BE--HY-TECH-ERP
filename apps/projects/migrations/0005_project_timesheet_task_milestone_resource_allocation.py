# Generated manually to preserve data through field renames.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_milestone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timesheet',
            old_name='hours',
            new_name='used_hours',
        ),
        migrations.RenameField(
            model_name='milestone',
            old_name='assignee',
            new_name='owner',
        ),
        migrations.RemoveField(
            model_name='milestone',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='milestone',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='milestone',
            name='due_date',
        ),
        migrations.AddField(
            model_name='milestone',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10),
        ),
        migrations.AddField(
            model_name='task',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='projects.project'),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=15),
        ),
        migrations.CreateModel(
            name='ResourceAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, max_length=100)),
                ('hours', models.DecimalField(decimal_places=2, help_text='Total hours allocated', max_digits=8)),
                ('allocated', models.DecimalField(decimal_places=2, help_text='Allocated %', max_digits=5)),
                ('availability', models.DecimalField(decimal_places=2, help_text='Availability %', max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_allocations', to='projects.project')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_allocations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

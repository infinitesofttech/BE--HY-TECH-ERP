from django.db import models
from django.conf import settings


class Project(models.Model):
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    STATUS_CHOICES = [
        ('active', 'Active'), ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=200)
    project_id = models.CharField(max_length=50, unique=True, blank=True)
    project_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True)
    project_timing = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium'
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active'
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    team_leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='led_projects'
    )
    responsible_persons = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.project_id:
            super().save(*args, **kwargs)
            self.project_id = f'PRJ{self.pk:04d}'
            super().save(update_fields=['project_id'])
        else:
            super().save(*args, **kwargs)


class Task(models.Model):
    CATEGORY_CHOICES = [
        ('call', 'Call'), ('email', 'Email'), ('meeting', 'Meeting'), ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    STATUS_CHOICES = [
        ('active', 'Active'), ('inactive', 'Inactive'),
    ]

    title = models.CharField(max_length=200)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True,
        related_name='tasks',
    )
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='other'
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='tasks'
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium'
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='active'
    )
    tags = models.CharField(max_length=500, blank=True)
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Milestone(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed'),
    ]

    milestone_id = models.CharField(max_length=50, unique=True, blank=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='milestones'
    )
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='milestones'
    )
    date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    progress = models.IntegerField(default=0, help_text='Completion %')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.milestone_id:
            super().save(*args, **kwargs)
            self.milestone_id = f'MLT{self.pk:04d}'
            super().save(update_fields=['milestone_id'])
        else:
            super().save(*args, **kwargs)


class TodoItem(models.Model):
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='todos'
    )
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=100, blank=True)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium'
    )
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_todos'
    )
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Timesheet(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timesheets'
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, blank=True
    )
    date = models.DateField()
    from_time = models.TimeField(null=True, blank=True)
    to_time = models.TimeField(null=True, blank=True)
    used_hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.email} - {self.used_hours}h'


class ResourceAllocation(models.Model):
    resource = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='resource_allocations',
    )
    role = models.CharField(max_length=100, blank=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='resource_allocations'
    )
    hours = models.DecimalField(
        max_digits=8, decimal_places=2, help_text='Total hours allocated',
    )
    allocated = models.DecimalField(
        max_digits=5, decimal_places=2, help_text='Allocated %',
    )
    availability = models.DecimalField(
        max_digits=5, decimal_places=2, help_text='Availability %',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.resource} - {self.project}'

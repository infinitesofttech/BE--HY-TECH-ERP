from django.db import models
from django.conf import settings


class PipelineStage(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    probability_default = models.IntegerField(default=0, help_text='Default probability %')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Lead(models.Model):
    LEAD_TYPE_CHOICES = [('person', 'Person'), ('company', 'Company')]
    STATUS_CHOICES = [
        ('new', 'New'), ('contacted', 'Contacted'), ('qualified', 'Qualified'),
        ('proposal', 'Proposal'), ('negotiation', 'Negotiation'),
        ('won', 'Won'), ('lost', 'Lost'),
    ]
    VISIBILITY_CHOICES = [('public', 'Public'), ('private', 'Private')]

    name = models.CharField(max_length=200)
    lead_type = models.CharField(max_length=10, choices=LEAD_TYPE_CHOICES, default='person')
    company_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    email_opt_out = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    phone_2 = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reviews = models.CharField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='leads/', null=True, blank=True)
    language = models.CharField(max_length=50, blank=True, default='English')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads'
    )
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated')
    source = models.ForeignKey(
        'masters.Source', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads'
    )
    industry = models.ForeignKey(
        'masters.Industry', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads'
    )
    currency = models.ForeignKey(
        'masters.Currency', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads'
    )
    contacts = models.ManyToManyField('contacts.Contact', blank=True, related_name='leads')
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    facebook = models.URLField(blank=True)
    skype = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    instagram = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Deal(models.Model):
    STAGE_CHOICES = [
        ('qualification', 'Qualification'), ('needs_analysis', 'Needs Analysis'),
        ('value_proposition', 'Value Proposition'), ('decision', 'Decision'),
        ('negotiation', 'Negotiation'), ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    STATUS_CHOICES = [('open', 'Open'), ('won', 'Won'), ('lost', 'Lost')]
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    PERIOD_CHOICES = [('days', 'Days'), ('month', 'Month')]

    name = models.CharField(max_length=200)
    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals'
    )
    contact = models.ForeignKey(
        'contacts.Contact', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deal_contacts'
    )
    company = models.ForeignKey(
        'contacts.Company', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deal_companies'
    )
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.ForeignKey(
        'masters.Currency', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deals'
    )
    pipeline_stage = models.ForeignKey(
        PipelineStage, on_delete=models.SET_NULL, null=True, blank=True
    )
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='qualification')
    probability = models.IntegerField(default=0, help_text='Probability %')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, blank=True)
    period_value = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    expected_close_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deals'
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='assigned_deals'
    )
    projects = models.ManyToManyField('projects.Project', blank=True, related_name='deals')
    source = models.ForeignKey(
        'masters.Source', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deals'
    )
    tags = models.CharField(max_length=500, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class DealActivity(models.Model):
    TYPE_CHOICES = [
        ('note', 'Note'), ('call', 'Call'), ('email', 'Email'),
        ('meeting', 'Meeting'), ('task', 'Task'),
    ]
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    attachment = models.FileField(
        upload_to='deal_attachments/', blank=True, null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_activity_type_display()} on {self.deal.name}'

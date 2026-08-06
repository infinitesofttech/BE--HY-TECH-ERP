from django.db import models
from django.conf import settings


class Company(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]
    VISIBILITY_CHOICES = [('public', 'Public'), ('private', 'Private')]

    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    email_opt_out = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    phone_2 = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    reviews = models.CharField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='companies/', null=True, blank=True)
    industry = models.ForeignKey(
        'masters.Industry', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='companies'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='companies'
    )
    tags = models.CharField(max_length=500, blank=True)
    deals = models.ManyToManyField(
        'pipeline.Deal', blank=True, related_name='related_companies'
    )
    source = models.ForeignKey(
        'masters.Source', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='companies'
    )
    contacts = models.ManyToManyField('Contact', blank=True, related_name='companies_list')
    language = models.CharField(max_length=50, blank=True, default='English')
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default='public'
    )
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Contact(models.Model):
    TYPE_CHOICES = [('person', 'Person'), ('business', 'Business')]
    VISIBILITY_CHOICES = [
        ('public', 'Public'), ('private', 'Private'), ('selected', 'Selected'),
    ]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    job_title = models.CharField(max_length=200, blank=True)
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='person',
        help_text='Person or business contact.',
    )
    about = models.TextField(blank=True, default='')
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='contact_list'
    )
    email = models.EmailField(blank=True)
    email_opt_out = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    phone_2 = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    deals = models.ManyToManyField(
        'pipeline.Deal', blank=True, related_name='related_contacts'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    reviews = models.CharField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='contacts/', null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='contacts'
    )
    tags = models.CharField(max_length=500, blank=True)
    source = models.ForeignKey(
        'masters.Source', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='contacts'
    )
    industry = models.ForeignKey(
        'masters.Industry', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='contacts'
    )
    language = models.CharField(max_length=50, blank=True, default='English')
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default='public'
    )
    visible_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='visible_contacts',
        help_text='People who can see this contact when visibility is "selected".',
    )
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'), ('read', 'Read'), ('replied', 'Replied'), ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.email}'

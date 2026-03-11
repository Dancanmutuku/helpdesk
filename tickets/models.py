from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import uuid


class Category(models.Model):
    HARDWARE = 'hardware'
    NETWORK = 'network'
    SOFTWARE = 'software'
    ACCOUNT = 'account'
    SECURITY = 'security'
    OTHER = 'other'

    TYPE_CHOICES = [
        (HARDWARE, 'Hardware'),
        (NETWORK, 'Network'),
        (SOFTWARE, 'Software'),
        (ACCOUNT, 'Account & Access'),
        (SECURITY, 'Security'),
        (OTHER, 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OTHER)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='tag', help_text='Bootstrap icon name')
    color = models.CharField(max_length=20, default='primary')
    auto_assign_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='auto_assigned_categories'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Ticket(models.Model):
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CRITICAL = 'critical'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]

    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_PENDING = 'pending'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    SOURCE_WEB = 'web'
    SOURCE_EMAIL = 'email'
    SOURCE_CHAT = 'chat'

    SOURCE_CHOICES = [
        (SOURCE_WEB, 'Web Form'),
        (SOURCE_EMAIL, 'Email'),
        (SOURCE_CHAT, 'Live Chat'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tickets')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_OPEN)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_WEB)

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets'
    )

    # SLA
    sla_due_at = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)
    first_response_at = models.DateTimeField(null=True, blank=True)

    # CSAT
    csat_score = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    csat_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    tags = models.ManyToManyField('Tag', blank=True, related_name='tickets')

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self._generate_ticket_id()
        if not self.sla_due_at and self.priority:
            hours = settings.SLA_RESPONSE_TIMES.get(self.priority, 24)
            self.sla_due_at = timezone.now() + timezone.timedelta(hours=hours)
        if self.status == self.STATUS_RESOLVED and not self.resolved_at:
            self.resolved_at = timezone.now()
        if self.status == self.STATUS_CLOSED and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args, **kwargs)

    def _generate_ticket_id(self):
        import random
        import string
        prefix = 'TKT'
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}-{suffix}"

    def get_absolute_url(self):
        return reverse('tickets:detail', kwargs={'ticket_id': self.ticket_id})

    def is_overdue(self):
        if self.sla_due_at and self.status not in [self.STATUS_RESOLVED, self.STATUS_CLOSED]:
            return timezone.now() > self.sla_due_at
        return False

    def sla_time_remaining(self):
        if self.sla_due_at and self.status not in [self.STATUS_RESOLVED, self.STATUS_CLOSED]:
            remaining = self.sla_due_at - timezone.now()
            return remaining
        return None

    def get_priority_color(self):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'orange',
            'critical': 'danger',
        }
        return colors.get(self.priority, 'secondary')

    def get_status_color(self):
        colors = {
            'open': 'primary',
            'in_progress': 'info',
            'pending': 'warning',
            'resolved': 'success',
            'closed': 'secondary',
        }
        return colors.get(self.status, 'secondary')

    def __str__(self):
        return f"[{self.ticket_id}] {self.title}"

    class Meta:
        ordering = ['-created_at']


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    is_internal = models.BooleanField(default=False, help_text='Internal note hidden from end users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        note_type = 'Internal Note' if self.is_internal else 'Reply'
        return f"{note_type} by {self.author} on {self.ticket.ticket_id}"

    class Meta:
        ordering = ['created_at']


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    field_changed = models.CharField(max_length=100)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.field_changed} changed"

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Ticket histories'


class CannedResponse(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

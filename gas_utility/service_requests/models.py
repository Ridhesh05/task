from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ServiceRequestCategory(models.Model):
    """Categories for service requests"""
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('active status'), default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('service request category')
        verbose_name_plural = _('service request categories')


class ServiceRequest(models.Model):
    """Service requests submitted by customers"""
    
    # Status choices
    STATUS_NEW = 'new'
    STATUS_ASSIGNED = 'assigned'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_NEW, _('New')),
        (STATUS_ASSIGNED, _('Assigned')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]
    
    # Priority choices
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, _('Low')),
        (PRIORITY_MEDIUM, _('Medium')),
        (PRIORITY_HIGH, _('High')),
        (PRIORITY_URGENT, _('Urgent')),
    ]
    
    # Fields
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    category = models.ForeignKey(
        ServiceRequestCategory, 
        verbose_name=_('category'),
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='service_requests'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('customer'),
        on_delete=models.CASCADE, 
        related_name='submitted_service_requests'
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('technician'),
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_service_requests'
    )
    status = models.CharField(
        _('status'),
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_NEW
    )
    priority = models.CharField(
        _('priority'),
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default=PRIORITY_MEDIUM
    )
    service_address = models.TextField(_('service address'))
    scheduled_date = models.DateField(_('scheduled date'), null=True, blank=True)
    scheduled_time_slot = models.CharField(_('time slot'), max_length=50, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    resolution_notes = models.TextField(_('resolution notes'), blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = _('service request')
        verbose_name_plural = _('service requests')
        ordering = ['-created_at']


class ServiceAttachment(models.Model):
    """Attachments for service requests"""
    service_request = models.ForeignKey(
        ServiceRequest, 
        verbose_name=_('service request'),
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(_('file'), upload_to='service_attachments/')
    file_name = models.CharField(_('file name'), max_length=255)
    file_type = models.CharField(_('file type'), max_length=100)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('uploaded by'),
        on_delete=models.SET_NULL, 
        null=True
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    def __str__(self):
        return self.file_name


class Comment(models.Model):
    """Comments on service requests"""
    service_request = models.ForeignKey(
        ServiceRequest, 
        verbose_name=_('service request'),
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('author'),
        on_delete=models.CASCADE
    )
    text = models.TextField(_('text'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.email} on {self.service_request.title}"
    
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['created_at']
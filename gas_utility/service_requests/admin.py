from django.contrib import admin
from .models import ServiceRequestCategory, ServiceRequest, ServiceAttachment, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class ServiceAttachmentInline(admin.TabularInline):
    model = ServiceAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(ServiceRequestCategory)
class ServiceRequestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'technician', 'category', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at', 'scheduled_date')
    search_fields = ('title', 'description', 'customer__email', 'technician__email', 'service_address')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [CommentInline, ServiceAttachmentInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category')
        }),
        ('Customer Information', {
            'fields': ('customer', 'service_address')
        }),
        ('Assignment', {
            'fields': ('technician', 'status', 'priority')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time_slot')
        }),
        ('Resolution', {
            'fields': ('resolution_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceAttachment)
class ServiceAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'service_request', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('file_name', 'service_request__title', 'uploaded_by__email')
    readonly_fields = ('uploaded_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'service_request', 'text_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__email', 'service_request__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'
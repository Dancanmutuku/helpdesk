from django.contrib import admin
from .models import Ticket, TicketReply, TicketAttachment, TicketHistory, Category, Tag, CannedResponse


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'auto_assign_to_safe']
    list_filter = ['type', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

    def auto_assign_to_safe(self, obj):
        return obj.auto_assign_to.get_full_name() if obj.auto_assign_to else '-'
    auto_assign_to_safe.short_description = 'Auto Assign To'


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    readonly_fields = ['created_at']


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_id_safe', 'title_safe', 'priority_safe', 'status_safe',
        'submitted_by_safe', 'assigned_to_safe', 'category_safe',
        'created_at', 'sla_breached'
    ]
    list_filter = ['status', 'priority', 'category', 'sla_breached', 'source']
    search_fields = ['ticket_id', 'title', 'description']
    readonly_fields = ['ticket_id', 'created_at', 'updated_at', 'sla_due_at', 'first_response_at']
    raw_id_fields = ['submitted_by', 'assigned_to']
    inlines = [TicketReplyInline, TicketAttachmentInline]
    date_hierarchy = 'created_at'
    list_per_page = 30

    # Safe getters
    def ticket_id_safe(self, obj):
        return getattr(obj, 'ticket_id', '-') or '-'
    ticket_id_safe.short_description = 'Ticket ID'

    def title_safe(self, obj):
        return getattr(obj, 'title', '-') or '-'
    title_safe.short_description = 'Title'

    def priority_safe(self, obj):
        return getattr(obj, 'priority', '-') or '-'
    priority_safe.short_description = 'Priority'

    def status_safe(self, obj):
        return getattr(obj, 'status', '-') or '-'
    status_safe.short_description = 'Status'

    def submitted_by_safe(self, obj):
        return obj.submitted_by.get_full_name() if obj.submitted_by else '-'
    submitted_by_safe.short_description = 'Submitted By'

    def assigned_to_safe(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else '-'
    assigned_to_safe.short_description = 'Assigned To'

    def category_safe(self, obj):
        return obj.category.name if obj.category else '-'
    category_safe.short_description = 'Category'


@admin.register(CannedResponse)
class CannedResponseAdmin(admin.ModelAdmin):
    list_display = ['title_safe', 'category_safe', 'is_active', 'created_by_safe']
    list_filter = ['is_active', 'category']

    def title_safe(self, obj):
        return obj.title or '-'
    title_safe.short_description = 'Title'

    def category_safe(self, obj):
        return obj.category.name if obj.category else '-'
    category_safe.short_description = 'Category'

    def created_by_safe(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else '-'
    created_by_safe.short_description = 'Created By'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
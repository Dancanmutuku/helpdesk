from django.contrib import admin
from .models import Ticket, TicketReply, TicketAttachment, TicketHistory, Category, Tag, CannedResponse


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'auto_assign_to']
    list_filter = ['type', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


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
    list_display = ['ticket_id', 'title', 'priority', 'status', 'submitted_by', 'assigned_to', 'category', 'created_at', 'sla_breached']
    list_filter = ['status', 'priority', 'category', 'sla_breached', 'source']
    search_fields = ['ticket_id', 'title', 'description']
    readonly_fields = ['ticket_id', 'created_at', 'updated_at', 'sla_due_at', 'first_response_at']
    raw_id_fields = ['submitted_by', 'assigned_to']
    inlines = [TicketReplyInline, TicketAttachmentInline]
    date_hierarchy = 'created_at'
    list_per_page = 30


@admin.register(CannedResponse)
class CannedResponseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_by']
    list_filter = ['is_active', 'category']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

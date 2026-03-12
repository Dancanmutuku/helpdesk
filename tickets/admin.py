from django.contrib import admin
from .models import (
    Ticket,
    TicketReply,
    TicketAttachment,
    TicketHistory,
    Category,
    Tag,
    CannedResponse,
)


# =====================================================
# CATEGORY ADMIN
# =====================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "is_active", "auto_assign_to_display")
    list_filter = ("type", "is_active")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Auto Assign To")
    def auto_assign_to_display(self, obj):
        if obj.auto_assign_to:
            return obj.auto_assign_to.get_full_name() or obj.auto_assign_to.username
        return "-"


# =====================================================
# INLINES
# =====================================================
class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    readonly_fields = ("created_at",)


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ("uploaded_at", "file_size")


# =====================================================
# TICKET ADMIN
# =====================================================
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        "ticket_id_display",
        "title_display",
        "priority_display",
        "status_display",
        "submitted_by_display",
        "assigned_to_display",
        "category_display",
        "created_at",
        "sla_breached_display",
    )

    list_filter = (
        "status",
        "priority",
        "category",
        "sla_breached",
        "source",
    )

    search_fields = ("ticket_id", "title", "description")

    readonly_fields = (
        "ticket_id",
        "created_at",
        "updated_at",
        "sla_due_at",
        "first_response_at",
    )

    raw_id_fields = ("submitted_by", "assigned_to")

    inlines = (TicketReplyInline, TicketAttachmentInline)

    date_hierarchy = "created_at"
    list_per_page = 30

    # ---------- SAFE DISPLAY METHODS ----------

    @admin.display(description="Ticket ID")
    def ticket_id_display(self, obj):
        return getattr(obj, "ticket_id", "-") or "-"

    @admin.display(description="Title")
    def title_display(self, obj):
        return getattr(obj, "title", "-") or "-"

    @admin.display(description="Priority")
    def priority_display(self, obj):
        return getattr(obj, "priority", "-") or "-"

    @admin.display(description="Status")
    def status_display(self, obj):
        return getattr(obj, "status", "-") or "-"

    @admin.display(description="Submitted By")
    def submitted_by_display(self, obj):
        if obj.submitted_by:
            return obj.submitted_by.get_full_name() or obj.submitted_by.username
        return "-"

    @admin.display(description="Assigned To")
    def assigned_to_display(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return "-"

    @admin.display(description="Category")
    def category_display(self, obj):
        return obj.category.name if obj.category else "-"

    @admin.display(boolean=True, description="SLA Breached")
    def sla_breached_display(self, obj):
        """
        Prevent admin crash if sla_breached is a property.
        """
        try:
            return bool(obj.sla_breached)
        except Exception:
            return False


# =====================================================
# CANNED RESPONSES
# =====================================================
@admin.register(CannedResponse)
class CannedResponseAdmin(admin.ModelAdmin):

    list_display = (
        "title_display",
        "category_display",
        "is_active",
        "created_by_display",
    )

    list_filter = ("is_active", "category")

    @admin.display(description="Title")
    def title_display(self, obj):
        return obj.title or "-"

    @admin.display(description="Category")
    def category_display(self, obj):
        return obj.category.name if obj.category else "-"

    @admin.display(description="Created By")
    def created_by_display(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "-"


# =====================================================
# TAG ADMIN
# =====================================================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
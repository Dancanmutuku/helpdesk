from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Department


# -----------------------------
# Department Admin
# -----------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


# -----------------------------
# Custom User Admin
# -----------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Display fields in the list
    list_display = [
        'username',
        'email',
        'full_name',
        'role',
        'department',
        'is_active',
        'avatar_tag',
    ]

    # Filters in the sidebar
    list_filter = ['role', 'department', 'is_active']

    # Search fields
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Add extra fields to change view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HelpDesk Profile', {
            'fields': ('role', 'department', 'phone', 'job_title', 'avatar', 'email_notifications')
        }),
    )

    # Add extra fields to add view
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('username', 'password1', 'password2', 'role', 'email', 'department')
        }),
    )

    # -----------------------------
    # Custom methods
    # -----------------------------
    @admin.display(description='Full Name')
    def full_name(self, obj):
        return obj.get_full_name() or obj.username

    @admin.display(description='Avatar')
    def avatar_tag(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:30px;height:30px;border-radius:50%;">',
                obj.avatar.url
            )
        return '-'
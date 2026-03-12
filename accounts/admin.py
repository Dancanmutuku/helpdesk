from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username_safe', 'email', 'full_name_safe', 'role', 'department_safe', 'is_active'
    ]
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('HelpDesk Profile', {
            'fields': ('role', 'department', 'phone', 'job_title', 'avatar', 'email_notifications')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('role', 'email', 'department')}),
    )

    # Safe methods
    def full_name_safe(self, obj):
        return obj.get_full_name() or obj.username
    full_name_safe.short_description = 'Full Name'

    def username_safe(self, obj):
        return obj.username or '-'
    username_safe.short_description = 'Username'

    def department_safe(self, obj):
        return obj.department.name if obj.department else '-'
    department_safe.short_description = 'Department'
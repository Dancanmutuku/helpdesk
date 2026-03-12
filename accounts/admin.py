from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department


# -----------------------------
# Department Admin
# -----------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


# -----------------------------
# Custom User Admin
# -----------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # ---- List Page ----
    list_display = (
        "username_display",
        "email",
        "full_name_display",
        "role",
        "department_display",
        "is_active",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = ("username",)

    # ---- Edit Page Sections ----
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "HelpDesk Profile",
            {
                "fields": (
                    "role",
                    "department",
                    "phone",
                    "job_title",
                    "avatar",
                    "email_notifications",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "role",
                    "email",
                    "department",
                )
            },
        ),
    )

    # -----------------------------
    # SAFE DISPLAY METHODS
    # -----------------------------

    @admin.display(description="Username")
    def username_display(self, obj):
        return obj.username or "-"

    @admin.display(description="Full Name")
    def full_name_display(self, obj):
        return obj.get_full_name() or obj.username

    @admin.display(description="Department")
    def department_display(self, obj):
        return obj.department.name if obj.department else "-"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AdminProfile, StudentProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Platform", {"fields": ("full_name", "role", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("email", "username", "full_name", "role", "is_staff")
    search_fields = ("email", "username", "full_name")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "eco_points", "current_streak", "longest_streak", "total_activities")
    search_fields = ("user__full_name", "user__email", "institution__name")
    list_filter = ("institution__location__state", "institution__location__district")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "admin_type", "institution")
    search_fields = ("user__full_name", "user__email")
    list_filter = ("admin_type",)

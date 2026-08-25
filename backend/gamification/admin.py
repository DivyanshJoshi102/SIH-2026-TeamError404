from django.contrib import admin

from .models import Badge, PointTransaction, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "criteria_type", "criteria_value", "is_active")
    list_filter = ("criteria_type", "is_active")
    search_fields = ("name", "description")


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "awarded_at")
    search_fields = ("user__full_name", "user__email", "badge__name")


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("student", "points", "source_type", "reference", "created_at")
    list_filter = ("source_type",)
    search_fields = ("student__full_name", "student__email", "reference")

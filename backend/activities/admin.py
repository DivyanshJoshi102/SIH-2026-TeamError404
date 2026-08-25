from django.contrib import admin

from .models import Activity, ActivityCompletion, ActivitySubmission, DailyActivity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "difficulty", "eco_points", "requires_proof", "is_active")
    list_filter = ("category", "difficulty", "requires_proof", "is_active")
    search_fields = ("title", "description")


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ("date", "activity")
    list_filter = ("date",)


@admin.register(ActivitySubmission)
class ActivitySubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "activity", "status", "submission_date", "verified_by")
    list_filter = ("status", "submission_date", "activity__category")
    search_fields = ("student__full_name", "student__email", "activity__title")


@admin.register(ActivityCompletion)
class ActivityCompletionAdmin(admin.ModelAdmin):
    list_display = ("student", "activity", "campaign", "date", "points_earned", "source")
    list_filter = ("source", "date")
    search_fields = ("student__full_name", "student__email", "activity__title", "campaign__title")

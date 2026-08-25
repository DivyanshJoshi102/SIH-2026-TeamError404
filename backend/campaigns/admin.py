from django.contrib import admin

from .models import Campaign, CampaignSubmission


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "eco_points", "is_active")
    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("title", "description")


@admin.register(CampaignSubmission)
class CampaignSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "campaign", "status", "submitted_at", "is_featured")
    list_filter = ("status", "is_featured", "campaign")
    search_fields = ("student__full_name", "student__email", "campaign__title")

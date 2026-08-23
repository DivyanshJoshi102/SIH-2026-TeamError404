from django.contrib import admin
from .models import Mission, Submission

admin.site.register(Mission)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'mission', 'is_approved', 'submitted_at')
    list_editable = ('is_approved',)
from django.conf import settings
from django.db import models


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    eco_points = models.PositiveIntegerField(default=40)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    requires_proof = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("start_date", "title")

    def __str__(self):
        return self.title


class CampaignSubmission(models.Model):
    class Statuses(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaign_submissions")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="submissions")
    proof_image = models.ImageField(upload_to="campaign_proofs/", null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Statuses.choices, default=Statuses.PENDING, db_index=True)
    submission_date = models.DateField(auto_now_add=True, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_campaign_submissions",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"{self.student.full_name} - {self.campaign.title}"

from django.conf import settings
from django.db import models
from django.utils import timezone


class Activity(models.Model):
    class Categories(models.TextChoices):
        WASTE_MANAGEMENT = "WASTE_MANAGEMENT", "Waste Management"
        WATER_CONSERVATION = "WATER_CONSERVATION", "Water Conservation"
        ENERGY = "ENERGY", "Energy"
        PLANTATION = "PLANTATION", "Plantation"
        CLEANLINESS = "CLEANLINESS", "Cleanliness"
        TRANSPORT = "TRANSPORT", "Transport"
        AWARENESS = "AWARENESS", "Awareness"

    class Difficulties(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=Categories.choices, db_index=True)
    difficulty = models.CharField(max_length=10, choices=Difficulties.choices, db_index=True)
    eco_points = models.PositiveIntegerField()
    requires_proof = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_activities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class DailyActivity(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="daily_assignments")
    date = models.DateField(unique=True, db_index=True)

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return f"{self.date} - {self.activity.title}"


class ActivitySubmission(models.Model):
    class Statuses(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_submissions")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="submissions")
    proof_image = models.ImageField(upload_to="activity_proofs/", null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Statuses.choices, default=Statuses.PENDING, db_index=True)
    submission_date = models.DateField(default=timezone.localdate, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_activity_submissions",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"{self.student.full_name} - {self.activity.title}"


class ActivityCompletion(models.Model):
    class SourceTypes(models.TextChoices):
        ACTIVITY = "ACTIVITY", "Activity"
        DAILY_ACTIVITY = "DAILY_ACTIVITY", "Daily Activity"
        CAMPAIGN = "CAMPAIGN", "Campaign"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_completions")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True, related_name="completions")
    campaign = models.ForeignKey("campaigns.Campaign", on_delete=models.CASCADE, null=True, blank=True, related_name="completions")
    date = models.DateField(db_index=True)
    points_earned = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=20, choices=SourceTypes.choices, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("student", "activity", "date"), name="unique_activity_completion_per_day"),
            models.UniqueConstraint(fields=("student", "campaign", "date"), name="unique_campaign_completion_per_day"),
        ]
        ordering = ("-date", "-created_at")

    def __str__(self):
        label = self.activity.title if self.activity_id else self.campaign.title
        return f"{self.student.full_name} - {label}"

from django.conf import settings
from django.db import models


class Badge(models.Model):
    class CriteriaTypes(models.TextChoices):
        ACTIVITY_COUNT = "ACTIVITY_COUNT", "Activity Count"
        CURRENT_STREAK = "CURRENT_STREAK", "Current Streak"
        CATEGORY_COUNT = "CATEGORY_COUNT", "Category Count"
        QUIZ_COUNT = "QUIZ_COUNT", "Quiz Count"
        CAMPAIGN_COUNT = "CAMPAIGN_COUNT", "Campaign Count"
        ECO_POINTS = "ECO_POINTS", "Eco Points"

    name = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, blank=True)
    criteria_type = models.CharField(max_length=30, choices=CriteriaTypes.choices)
    criteria_value = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("criteria_value", "name")

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="user_badges")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "badge"), name="unique_user_badge")
        ]
        ordering = ("-awarded_at",)

    def __str__(self):
        return f"{self.user.full_name} - {self.badge.name}"


class PointTransaction(models.Model):
    class SourceTypes(models.TextChoices):
        ACTIVITY = "ACTIVITY", "Activity"
        QUIZ = "QUIZ", "Quiz"
        CAMPAIGN = "CAMPAIGN", "Campaign"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="point_transactions")
    points = models.PositiveIntegerField()
    source_type = models.CharField(max_length=20, choices=SourceTypes.choices)
    reference = models.CharField(max_length=120, unique=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.student.full_name} +{self.points}"

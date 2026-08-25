from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    institution = models.ForeignKey("institutions.Institution", on_delete=models.PROTECT, related_name="students")
    eco_points = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_activities = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.institution.name}"


class AdminProfile(models.Model):
    class AdminTypes(models.TextChoices):
        TEACHER = "TEACHER", "Teacher"
        ECO_CLUB = "ECO_CLUB", "Eco Club"
        NGO = "NGO", "NGO"
        GOVERNMENT = "GOVERNMENT", "Government"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    admin_type = models.CharField(max_length=20, choices=AdminTypes.choices)
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_profiles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.admin_type})"

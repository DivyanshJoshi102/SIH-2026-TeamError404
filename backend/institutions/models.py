from django.db import models


class Location(models.Model):
    state = models.CharField(max_length=120, db_index=True)
    district = models.CharField(max_length=120, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("state", "district"), name="unique_state_district")
        ]
        ordering = ("state", "district")

    def __str__(self):
        return f"{self.district}, {self.state}"


class Institution(models.Model):
    class InstitutionTypes(models.TextChoices):
        SCHOOL = "SCHOOL", "School"
        COLLEGE = "COLLEGE", "College"

    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=InstitutionTypes.choices)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="institutions")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

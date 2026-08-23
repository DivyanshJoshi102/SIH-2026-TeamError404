from django.db import models
from django.contrib.auth.models import User

class Mission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.IntegerField(default=50)

    def __str__(self):
        return self.title

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    proof_photo = models.ImageField(upload_to='proofs/')
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.mission.title}"
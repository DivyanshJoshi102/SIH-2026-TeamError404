from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from gamification.models import Badge, PointTransaction, UserBadge
from institutions.models import Institution, Location
from users.models import AdminProfile, StudentProfile, User

from .models import Activity, ActivityCompletion, ActivitySubmission


def test_image(name="proof.png"):
    buffer = BytesIO()
    Image.new("RGB", (20, 20), color="green").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


class ActivityFlowTests(APITestCase):
    def setUp(self):
        location = Location.objects.create(state="Uttarakhand", district="Dehradun")
        institution = Institution.objects.create(
            name="Activity Test College",
            type=Institution.InstitutionTypes.COLLEGE,
            location=location,
        )
        self.student = User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="Student@123",
            full_name="Student One",
            role=User.Roles.STUDENT,
        )
        StudentProfile.objects.create(user=self.student, institution=institution)

        self.admin = User.objects.create_user(
            username="teacher1",
            email="teacher1@test.com",
            password="Teacher@123",
            full_name="Teacher One",
            role=User.Roles.ADMIN,
        )
        AdminProfile.objects.create(
            user=self.admin,
            admin_type=AdminProfile.AdminTypes.TEACHER,
            institution=institution,
        )

        Badge.objects.create(
            name="First Step",
            description="Complete one activity.",
            criteria_type=Badge.CriteriaTypes.ACTIVITY_COUNT,
            criteria_value=1,
        )

        self.activity = Activity.objects.create(
            title="Plant a Tree",
            description="Plant and upload proof.",
            category=Activity.Categories.PLANTATION,
            difficulty=Activity.Difficulties.MEDIUM,
            eco_points=25,
            requires_proof=True,
            created_by=self.admin,
        )

    def test_submission_approval_awards_points_once_and_badge(self):
        self.client.force_authenticate(self.student)
        submit_response = self.client.post(
            f"/api/activities/{self.activity.id}/submit/",
            {
                "description": "Planted one neem sapling.",
                "proof_image": test_image(),
            },
        )
        self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)
        submission = ActivitySubmission.objects.get()
        self.assertEqual(submission.status, ActivitySubmission.Statuses.PENDING)

        self.client.force_authenticate(self.admin)
        review_response = self.client.post(
            f"/api/activities/submissions/{submission.id}/review/",
            {"action": "APPROVE"},
            format="json",
        )
        self.assertEqual(review_response.status_code, status.HTTP_200_OK)

        self.student.student_profile.refresh_from_db()
        self.assertEqual(self.student.student_profile.eco_points, 25)
        self.assertEqual(ActivityCompletion.objects.count(), 1)
        self.assertEqual(PointTransaction.objects.count(), 1)
        self.assertTrue(UserBadge.objects.filter(user=self.student, badge__name="First Step").exists())

        second_review = self.client.post(
            f"/api/activities/submissions/{submission.id}/review/",
            {"action": "APPROVE"},
            format="json",
        )
        self.assertEqual(second_review.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PointTransaction.objects.count(), 1)

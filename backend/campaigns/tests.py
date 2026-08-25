from datetime import timedelta
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from institutions.models import Institution, Location
from users.models import AdminProfile, StudentProfile, User

from .models import Campaign, CampaignSubmission


def campaign_image(name="campaign.png"):
    buffer = BytesIO()
    Image.new("RGB", (20, 20), color="blue").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


class CampaignFlowTests(APITestCase):
    def setUp(self):
        location = Location.objects.create(state="Uttarakhand", district="Dehradun")
        institution = Institution.objects.create(
            name="Campaign Test College",
            type=Institution.InstitutionTypes.COLLEGE,
            location=location,
        )
        self.student = User.objects.create_user(
            username="campaignstudent",
            email="campaignstudent@test.com",
            password="Student@123",
            full_name="Campaign Student",
            role=User.Roles.STUDENT,
        )
        StudentProfile.objects.create(user=self.student, institution=institution)

        self.admin = User.objects.create_user(
            username="campaignadmin",
            email="campaignadmin@test.com",
            password="Teacher@123",
            full_name="Campaign Admin",
            role=User.Roles.ADMIN,
        )
        AdminProfile.objects.create(
            user=self.admin,
            admin_type=AdminProfile.AdminTypes.TEACHER,
            institution=institution,
        )

        today = timezone.localdate()
        self.campaign = Campaign.objects.create(
            title="Plastic-Free Week",
            description="Avoid single-use plastic for one week.",
            eco_points=40,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=7),
            created_by=self.admin,
        )

    def test_campaign_approval_awards_points(self):
        self.client.force_authenticate(self.student)
        submit_response = self.client.post(
            f"/api/campaigns/{self.campaign.id}/submit/",
            {
                "description": "Used steel bottle and cloth bag.",
                "proof_image": campaign_image(),
            },
        )
        self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)
        submission = CampaignSubmission.objects.get()
        self.assertEqual(submission.status, CampaignSubmission.Statuses.PENDING)

        self.client.force_authenticate(self.admin)
        review_response = self.client.post(
            f"/api/campaigns/submissions/{submission.id}/review/",
            {"action": "APPROVE", "is_featured": True},
            format="json",
        )
        self.assertEqual(review_response.status_code, status.HTTP_200_OK)
        self.student.student_profile.refresh_from_db()
        self.assertEqual(self.student.student_profile.eco_points, 40)

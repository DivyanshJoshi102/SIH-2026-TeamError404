from rest_framework import status
from rest_framework.test import APITestCase

from institutions.models import Institution, Location
from users.models import StudentProfile, User


class AuthenticationTests(APITestCase):
    def setUp(self):
        location = Location.objects.create(state="Uttarakhand", district="Dehradun")
        self.institution = Institution.objects.create(
            name="Graphic Era Test College",
            type=Institution.InstitutionTypes.COLLEGE,
            location=location,
        )

    def test_student_registration_and_login(self):
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "student@test.com",
                "password": "Student@123",
                "full_name": "Test Student",
                "role": User.Roles.STUDENT,
                "institution_id": self.institution.id,
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StudentProfile.objects.filter(user__email="student@test.com").exists())

        token_response = self.client.post(
            "/api/auth/token/",
            {
                "email": "student@test.com",
                "password": "Student@123",
            },
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

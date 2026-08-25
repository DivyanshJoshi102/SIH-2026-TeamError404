from rest_framework import status
from rest_framework.test import APITestCase

from institutions.models import Institution, Location
from users.models import StudentProfile, User

from .models import Question, Quiz, QuizAttempt


class QuizFlowTests(APITestCase):
    def setUp(self):
        location = Location.objects.create(state="Uttarakhand", district="Dehradun")
        institution = Institution.objects.create(
            name="Quiz Test College",
            type=Institution.InstitutionTypes.COLLEGE,
            location=location,
        )
        self.student = User.objects.create_user(
            username="quizstudent",
            email="quizstudent@test.com",
            password="Student@123",
            full_name="Quiz Student",
            role=User.Roles.STUDENT,
        )
        StudentProfile.objects.create(user=self.student, institution=institution)

        self.quiz = Quiz.objects.create(title="Climate Basics", description="Quick quiz", eco_points=20)
        self.question_one = Question.objects.create(
            quiz=self.quiz,
            prompt="Which bin is used for wet waste?",
            options=["Blue", "Green", "Red", "Black"],
            correct_option=1,
        )
        self.question_two = Question.objects.create(
            quiz=self.quiz,
            prompt="Which gas traps heat in the atmosphere?",
            options=["Hydrogen", "Carbon Dioxide", "Neon", "Helium"],
            correct_option=1,
        )

    def test_quiz_scores_and_prevents_point_farming(self):
        self.client.force_authenticate(self.student)
        first_response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {
                "answers": {
                    str(self.question_one.id): 1,
                    str(self.question_two.id): 0,
                }
            },
            format="json",
        )
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        first_attempt = QuizAttempt.objects.get()
        self.assertEqual(first_attempt.score, 1)
        self.assertEqual(first_attempt.earned_points, 10)
        self.student.student_profile.refresh_from_db()
        self.assertEqual(self.student.student_profile.eco_points, 10)

        second_response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {
                "answers": {
                    str(self.question_one.id): 1,
                    str(self.question_two.id): 1,
                }
            },
            format="json",
        )
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(QuizAttempt.objects.count(), 2)
        self.student.student_profile.refresh_from_db()
        self.assertEqual(self.student.student_profile.eco_points, 10)

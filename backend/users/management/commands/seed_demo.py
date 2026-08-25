from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from activities.models import Activity, DailyActivity
from campaigns.models import Campaign
from gamification.models import Badge
from institutions.models import Institution, Location
from quizzes.models import Question, Quiz
from users.models import AdminProfile, StudentProfile, User


class Command(BaseCommand):
    help = "Seed demo data for the SIH environmental education platform."

    def handle(self, *args, **options):
        today = timezone.localdate()

        dehradun, _ = Location.objects.get_or_create(state="Uttarakhand", district="Dehradun")
        bhopal, _ = Location.objects.get_or_create(state="Madhya Pradesh", district="Bhopal")

        institution_one, _ = Institution.objects.get_or_create(
            name="Graphic Era University",
            defaults={"type": Institution.InstitutionTypes.COLLEGE, "location": dehradun},
        )
        institution_two, _ = Institution.objects.get_or_create(
            name="Government Excellence School Bhopal",
            defaults={"type": Institution.InstitutionTypes.SCHOOL, "location": bhopal},
        )

        admin_user, admin_created = User.objects.get_or_create(
            email="teacher@example.com",
            defaults={
                "username": "teacher",
                "full_name": "Demo Teacher",
                "role": User.Roles.ADMIN,
                "is_staff": True,
            },
        )
        if admin_created:
            admin_user.set_password("Teacher@123")
            admin_user.save(update_fields=["password"])
        AdminProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                "admin_type": AdminProfile.AdminTypes.TEACHER,
                "institution": institution_one,
            },
        )

        student_user, student_created = User.objects.get_or_create(
            email="student@example.com",
            defaults={
                "username": "student",
                "full_name": "Demo Student",
                "role": User.Roles.STUDENT,
            },
        )
        if student_created:
            student_user.set_password("Student@123")
            student_user.save(update_fields=["password"])
        StudentProfile.objects.get_or_create(user=student_user, defaults={"institution": institution_one})

        second_student, second_student_created = User.objects.get_or_create(
            email="student2@example.com",
            defaults={
                "username": "student2",
                "full_name": "Second Demo Student",
                "role": User.Roles.STUDENT,
            },
        )
        if second_student_created:
            second_student.set_password("Student@123")
            second_student.save(update_fields=["password"])
        StudentProfile.objects.get_or_create(user=second_student, defaults={"institution": institution_two})

        activity_one, _ = Activity.objects.get_or_create(
            title="Plant a Tree",
            defaults={
                "description": "Plant a sapling nearby and upload a proof image.",
                "category": Activity.Categories.PLANTATION,
                "difficulty": Activity.Difficulties.MEDIUM,
                "eco_points": 25,
                "requires_proof": True,
                "created_by": admin_user,
            },
        )
        Activity.objects.get_or_create(
            title="Switch Off Unused Lights",
            defaults={
                "description": "Track and switch off unnecessary lights at home for a day.",
                "category": Activity.Categories.ENERGY,
                "difficulty": Activity.Difficulties.EASY,
                "eco_points": 10,
                "requires_proof": False,
                "created_by": admin_user,
            },
        )
        Activity.objects.get_or_create(
            title="Segregate Household Waste",
            defaults={
                "description": "Separate wet and dry waste and share what changed in your routine.",
                "category": Activity.Categories.WASTE_MANAGEMENT,
                "difficulty": Activity.Difficulties.EASY,
                "eco_points": 15,
                "requires_proof": True,
                "created_by": admin_user,
            },
        )
        DailyActivity.objects.update_or_create(date=today, defaults={"activity": activity_one})

        quiz, _ = Quiz.objects.get_or_create(
            title="Climate Basics",
            defaults={
                "description": "A short intro quiz on climate change and sustainability.",
                "eco_points": 20,
                "created_by": admin_user,
            },
        )
        if not quiz.questions.exists():
            Question.objects.bulk_create(
                [
                    Question(
                        quiz=quiz,
                        prompt="Which gas is the biggest contributor to global warming?",
                        options=["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"],
                        correct_option=1,
                    ),
                    Question(
                        quiz=quiz,
                        prompt="Which waste bin is commonly used for wet waste?",
                        options=["Blue", "Green", "Black", "Red"],
                        correct_option=1,
                    ),
                ]
            )

        Campaign.objects.get_or_create(
            title="Plastic-Free Week",
            defaults={
                "description": "Avoid single-use plastic for one week and share your progress.",
                "eco_points": 40,
                "start_date": today - timedelta(days=1),
                "end_date": today + timedelta(days=7),
                "requires_proof": True,
                "created_by": admin_user,
            },
        )

        badge_defaults = [
            {
                "name": "First Step",
                "description": "Complete your first eco action.",
                "criteria_type": Badge.CriteriaTypes.ACTIVITY_COUNT,
                "criteria_value": 1,
                "icon": "leaf",
            },
            {
                "name": "Eco Warrior",
                "description": "Complete 10 eco actions.",
                "criteria_type": Badge.CriteriaTypes.ACTIVITY_COUNT,
                "criteria_value": 10,
                "icon": "shield",
            },
            {
                "name": "Green Streak",
                "description": "Maintain a 7-day streak.",
                "criteria_type": Badge.CriteriaTypes.CURRENT_STREAK,
                "criteria_value": 7,
                "icon": "flame",
            },
            {
                "name": "Tree Guardian",
                "description": "Complete 5 plantation actions.",
                "criteria_type": Badge.CriteriaTypes.CATEGORY_COUNT,
                "criteria_value": 5,
                "metadata": {"category": Activity.Categories.PLANTATION},
                "icon": "tree",
            },
        ]
        for badge in badge_defaults:
            Badge.objects.get_or_create(name=badge["name"], defaults=badge)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Student login: student@example.com / Student@123")
        self.stdout.write("Admin login: teacher@example.com / Teacher@123")

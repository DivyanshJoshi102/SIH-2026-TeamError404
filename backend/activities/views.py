from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView

from config.api import success_response
from users.permissions import IsAdminRole, IsStudent

from .models import Activity, ActivitySubmission, DailyActivity
from .serializers import (
    ActivitySerializer,
    ActivitySubmissionCreateSerializer,
    ActivitySubmissionReviewSerializer,
    ActivitySubmissionSerializer,
)
from .services import review_activity_submission, submit_activity


class ActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.filter(is_active=True)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Activity.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        difficulty = self.request.query_params.get("difficulty")
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DailyActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        daily_activity = DailyActivity.objects.select_related("activity").filter(date=today).first()
        if not daily_activity:
            return success_response(
                {"activity": None, "date": today, "completed": False},
                message="No daily activity is set for today.",
            )

        completed = ActivitySubmission.objects.filter(
            student=request.user,
            activity=daily_activity.activity,
            submission_date=today,
        ).exclude(status=ActivitySubmission.Statuses.REJECTED).exists()
        return success_response(
            {
                "activity": ActivitySerializer(daily_activity.activity).data,
                "date": today,
                "completed": completed,
            }
        )


class ActivitySubmitView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, activity_id):
        activity = generics.get_object_or_404(Activity, pk=activity_id)
        serializer = ActivitySubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = submit_activity(
            request.user,
            activity,
            description=serializer.validated_data.get("description", ""),
            proof_image=serializer.validated_data.get("proof_image"),
        )
        return success_response(
            ActivitySubmissionSerializer(submission).data,
            message="Activity submitted successfully.",
            status=status.HTTP_201_CREATED,
        )


class StudentSubmissionListView(generics.ListAPIView):
    permission_classes = [IsStudent]
    serializer_class = ActivitySubmissionSerializer

    def get_queryset(self):
        return ActivitySubmission.objects.filter(student=self.request.user).select_related("activity")


class AdminSubmissionListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = ActivitySubmissionSerializer

    def get_queryset(self):
        queryset = ActivitySubmission.objects.select_related("activity", "student__student_profile__institution")
        status_filter = self.request.query_params.get("status")
        admin_profile = self.request.user.admin_profile

        if admin_profile.institution_id:
            queryset = queryset.filter(student__student_profile__institution_id=admin_profile.institution_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class ActivitySubmissionReviewView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, submission_id):
        submission = generics.get_object_or_404(ActivitySubmission, pk=submission_id)
        serializer = ActivitySubmissionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reviewed_submission = review_activity_submission(
            submission,
            request.user,
            approve=serializer.validated_data["action"] == "APPROVE",
            rejection_reason=serializer.validated_data.get("rejection_reason", ""),
        )
        return success_response(ActivitySubmissionSerializer(reviewed_submission).data, message="Submission reviewed successfully.")

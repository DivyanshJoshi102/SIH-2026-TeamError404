from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView

from config.api import success_response
from users.permissions import IsAdminRole, IsStudent

from .models import Campaign, CampaignSubmission
from .serializers import (
    CampaignSerializer,
    CampaignSubmissionCreateSerializer,
    CampaignSubmissionReviewSerializer,
    CampaignSubmissionSerializer,
)
from .services import review_campaign_submission, submit_campaign


class CampaignListCreateView(generics.ListCreateAPIView):
    serializer_class = CampaignSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Campaign.objects.filter(is_active=True).order_by("start_date")
        if self.request.query_params.get("active") == "true":
            today = timezone.localdate()
            queryset = queryset.filter(start_date__lte=today, end_date__gte=today)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CampaignSubmitView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, campaign_id):
        campaign = generics.get_object_or_404(Campaign, pk=campaign_id)
        serializer = CampaignSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = submit_campaign(
            request.user,
            campaign,
            description=serializer.validated_data.get("description", ""),
            proof_image=serializer.validated_data.get("proof_image"),
        )
        return success_response(
            CampaignSubmissionSerializer(submission).data,
            message="Campaign submitted successfully.",
            status=status.HTTP_201_CREATED,
        )


class StudentCampaignSubmissionListView(generics.ListAPIView):
    permission_classes = [IsStudent]
    serializer_class = CampaignSubmissionSerializer

    def get_queryset(self):
        return CampaignSubmission.objects.filter(student=self.request.user).select_related("campaign")


class AdminCampaignSubmissionListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CampaignSubmissionSerializer

    def get_queryset(self):
        queryset = CampaignSubmission.objects.select_related("campaign", "student__student_profile__institution")
        admin_profile = self.request.user.admin_profile
        status_filter = self.request.query_params.get("status")
        if admin_profile.institution_id:
            queryset = queryset.filter(student__student_profile__institution_id=admin_profile.institution_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class CampaignSubmissionReviewView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, submission_id):
        submission = generics.get_object_or_404(CampaignSubmission, pk=submission_id)
        serializer = CampaignSubmissionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reviewed_submission = review_campaign_submission(
            submission,
            request.user,
            approve=serializer.validated_data["action"] == "APPROVE",
            rejection_reason=serializer.validated_data.get("rejection_reason", ""),
            is_featured=serializer.validated_data.get("is_featured", False),
        )
        return success_response(
            CampaignSubmissionSerializer(reviewed_submission).data,
            message="Campaign submission reviewed successfully.",
        )


class FeaturedCampaignSubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        featured = CampaignSubmission.objects.filter(
            status=CampaignSubmission.Statuses.APPROVED,
            is_featured=True,
        ).select_related("campaign").first()
        if featured is None:
            featured = CampaignSubmission.objects.filter(
                status=CampaignSubmission.Statuses.APPROVED,
                campaign__is_active=True,
            ).select_related("campaign").order_by("?").first()
        return success_response(
            CampaignSubmissionSerializer(featured).data if featured else None,
            message="Featured campaign submission fetched successfully.",
        )

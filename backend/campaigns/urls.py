from django.urls import path

from .views import (
    AdminCampaignSubmissionListView,
    CampaignListCreateView,
    CampaignSubmissionReviewView,
    CampaignSubmitView,
    FeaturedCampaignSubmissionView,
    StudentCampaignSubmissionListView,
)

urlpatterns = [
    path("", CampaignListCreateView.as_view(), name="campaign-list"),
    path("featured/", FeaturedCampaignSubmissionView.as_view(), name="campaign-featured"),
    path("submissions/", StudentCampaignSubmissionListView.as_view(), name="student-campaign-submissions"),
    path("admin/submissions/", AdminCampaignSubmissionListView.as_view(), name="admin-campaign-submissions"),
    path("submissions/<int:submission_id>/review/", CampaignSubmissionReviewView.as_view(), name="campaign-submission-review"),
    path("<int:campaign_id>/submit/", CampaignSubmitView.as_view(), name="campaign-submit"),
]

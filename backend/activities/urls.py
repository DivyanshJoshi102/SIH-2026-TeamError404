from django.urls import path

from .views import (
    ActivityListCreateView,
    ActivitySubmissionReviewView,
    ActivitySubmitView,
    AdminSubmissionListView,
    DailyActivityView,
    StudentSubmissionListView,
)

urlpatterns = [
    path("", ActivityListCreateView.as_view(), name="activity-list"),
    path("daily/", DailyActivityView.as_view(), name="daily-activity"),
    path("submissions/", StudentSubmissionListView.as_view(), name="student-activity-submissions"),
    path("admin/submissions/", AdminSubmissionListView.as_view(), name="admin-activity-submissions"),
    path("submissions/<int:submission_id>/review/", ActivitySubmissionReviewView.as_view(), name="activity-submission-review"),
    path("<int:activity_id>/submit/", ActivitySubmitView.as_view(), name="activity-submit"),
]

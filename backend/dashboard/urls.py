from django.urls import path

from .views import AdminDashboardView, LeaderboardView, StudentDashboardView

urlpatterns = [
    path("student/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
]

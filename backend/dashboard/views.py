from rest_framework.views import APIView

from config.api import success_response
from users.permissions import IsAdminRole, IsStudent

from .serializers import LeaderboardQuerySerializer
from .services import get_admin_dashboard, get_leaderboard, get_student_dashboard


class StudentDashboardView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return success_response(get_student_dashboard(request.user))


class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return success_response(get_admin_dashboard(request.user))


class LeaderboardView(APIView):
    def get(self, request):
        serializer = LeaderboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = get_leaderboard(
            request.user,
            serializer.validated_data["scope"],
            serializer.validated_data["period"],
        )
        return success_response(
            {
                "scope": serializer.validated_data["scope"],
                "period": serializer.validated_data["period"],
                "results": data,
            }
        )

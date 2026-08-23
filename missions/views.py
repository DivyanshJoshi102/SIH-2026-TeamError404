from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Mission, Submission
from .serializers import SubmissionSerializer

User = get_user_model()


class DashboardDataView(APIView):
    def get(self, request):
        recent_submissions = Submission.objects.select_related('student', 'mission').order_by('-id')[:5]

        data = {
            "stats": {
                "total_users": User.objects.count(),
                "total_missions": Mission.objects.count(),
                "total_submissions": Submission.objects.count(),
                "approved_submissions": Submission.objects.filter(is_approved=True).count(),
                "pending_submissions": Submission.objects.filter(is_approved=False).count(),
            },
            "recent_submissions": SubmissionSerializer(recent_submissions, many=True).data
        }
        return Response(data)
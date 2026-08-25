from rest_framework import generics
from rest_framework.views import APIView

from config.api import success_response
from users.permissions import IsStudent

from .models import Quiz
from .serializers import QuizAttemptSerializer, QuizDetailSerializer, QuizSerializer, QuizSubmissionSerializer
from .services import submit_quiz


class QuizListView(generics.ListAPIView):
    permission_classes = [IsStudent]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.filter(is_active=True)


class QuizDetailView(generics.RetrieveAPIView):
    permission_classes = [IsStudent]
    serializer_class = QuizDetailSerializer
    queryset = Quiz.objects.filter(is_active=True).prefetch_related("questions")


class QuizSubmitView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, quiz_id):
        quiz = generics.get_object_or_404(Quiz.objects.prefetch_related("questions"), pk=quiz_id, is_active=True)
        serializer = QuizSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = submit_quiz(request.user, quiz, serializer.validated_data["answers"])
        return success_response(
            QuizAttemptSerializer(attempt).data,
            message="Quiz submitted successfully.",
        )

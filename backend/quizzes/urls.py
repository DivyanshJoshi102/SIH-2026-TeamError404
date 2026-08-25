from django.urls import path

from .views import QuizDetailView, QuizListView, QuizSubmitView

urlpatterns = [
    path("", QuizListView.as_view(), name="quiz-list"),
    path("<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("<int:quiz_id>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
]

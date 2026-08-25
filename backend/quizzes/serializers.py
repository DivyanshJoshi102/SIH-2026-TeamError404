from rest_framework import serializers

from .models import Question, Quiz, QuizAttempt


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "prompt", "options")


class QuizSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(source="questions.count", read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "title", "description", "eco_points", "questions_count")


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "title", "description", "eco_points", "questions")


class QuizSubmissionSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.IntegerField(), allow_empty=False)


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ("id", "quiz", "score", "total_questions", "earned_points", "is_reward_attempt", "submitted_at")

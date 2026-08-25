from django.db import transaction
from rest_framework import serializers

from gamification.models import PointTransaction
from gamification.services import evaluate_badges

from .models import QuizAttempt


@transaction.atomic
def submit_quiz(student, quiz, answers):
    questions = list(quiz.questions.all())
    if not questions:
        raise serializers.ValidationError({"quiz": ["This quiz has no questions yet."]})

    correct_answers = 0
    for question in questions:
        submitted_answer = answers.get(str(question.id))
        if submitted_answer is None:
            continue
        if int(submitted_answer) == question.correct_option:
            correct_answers += 1

    is_first_reward_attempt = not QuizAttempt.objects.filter(
        student=student,
        quiz=quiz,
        is_reward_attempt=True,
    ).exists()
    earned_points = round((quiz.eco_points * correct_answers) / len(questions)) if is_first_reward_attempt else 0

    attempt = QuizAttempt.objects.create(
        student=student,
        quiz=quiz,
        answers=answers,
        score=correct_answers,
        total_questions=len(questions),
        earned_points=earned_points,
        is_reward_attempt=is_first_reward_attempt,
    )

    if is_first_reward_attempt and earned_points > 0:
        from gamification.services import award_points

        award_points(
            student,
            earned_points,
            PointTransaction.SourceTypes.QUIZ,
            f"quiz-attempt:{attempt.id}",
            {"quiz_id": quiz.id},
        )

    evaluate_badges(student)
    return attempt

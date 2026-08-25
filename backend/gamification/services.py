from datetime import timedelta

from django.db import transaction
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from activities.models import ActivityCompletion

from .models import Badge, PointTransaction, UserBadge


@transaction.atomic
def award_points(student, points, source_type, reference, metadata=None):
    transaction_record, created = PointTransaction.objects.get_or_create(
        reference=reference,
        defaults={
            "student": student,
            "points": points,
            "source_type": source_type,
            "metadata": metadata or {},
        },
    )
    if created:
        student.student_profile.__class__.objects.filter(pk=student.student_profile.pk).update(
            eco_points=F("eco_points") + points
        )
        student.student_profile.refresh_from_db(fields=["eco_points"])
    return transaction_record, created


def refresh_profile_totals(student):
    completion_queryset = ActivityCompletion.objects.filter(student=student)
    distinct_dates = list(
        completion_queryset.values_list("date", flat=True).distinct().order_by("date")
    )

    if not distinct_dates:
        student.student_profile.__class__.objects.filter(pk=student.student_profile.pk).update(
            current_streak=0,
            longest_streak=0,
            total_activities=0,
        )
        student.student_profile.refresh_from_db(fields=["current_streak", "longest_streak", "total_activities"])
        return

    longest_streak = 1
    rolling_streak = 1

    for previous, current in zip(distinct_dates, distinct_dates[1:]):
        if current == previous + timedelta(days=1):
            rolling_streak += 1
            longest_streak = max(longest_streak, rolling_streak)
        else:
            rolling_streak = 1

    current_streak = 1
    for index in range(len(distinct_dates) - 1, 0, -1):
        if distinct_dates[index] == distinct_dates[index - 1] + timedelta(days=1):
            current_streak += 1
        else:
            break

    student.student_profile.__class__.objects.filter(pk=student.student_profile.pk).update(
        current_streak=current_streak,
        longest_streak=max(longest_streak, current_streak),
        total_activities=completion_queryset.count(),
        eco_points=Coalesce(
            PointTransaction.objects.filter(student=student).aggregate(total=Sum("points"))["total"],
            0,
        ),
    )
    student.student_profile.refresh_from_db(fields=["current_streak", "longest_streak", "total_activities", "eco_points"])


def evaluate_badges(student):
    from quizzes.models import QuizAttempt

    refresh_profile_totals(student)

    total_activities = ActivityCompletion.objects.filter(student=student).count()
    campaign_count = ActivityCompletion.objects.filter(student=student, source=ActivityCompletion.SourceTypes.CAMPAIGN).count()
    rewarded_quiz_count = QuizAttempt.objects.filter(student=student, earned_points__gt=0).values("quiz_id").distinct().count()

    awarded_badges = []
    for badge in Badge.objects.filter(is_active=True):
        qualifies = False
        if badge.criteria_type == Badge.CriteriaTypes.ACTIVITY_COUNT:
            qualifies = total_activities >= badge.criteria_value
        elif badge.criteria_type == Badge.CriteriaTypes.CURRENT_STREAK:
            qualifies = student.student_profile.current_streak >= badge.criteria_value
        elif badge.criteria_type == Badge.CriteriaTypes.CATEGORY_COUNT:
            category = badge.metadata.get("category")
            qualifies = (
                ActivityCompletion.objects.filter(student=student, activity__category=category).count()
                >= badge.criteria_value
            )
        elif badge.criteria_type == Badge.CriteriaTypes.QUIZ_COUNT:
            qualifies = rewarded_quiz_count >= badge.criteria_value
        elif badge.criteria_type == Badge.CriteriaTypes.CAMPAIGN_COUNT:
            qualifies = campaign_count >= badge.criteria_value
        elif badge.criteria_type == Badge.CriteriaTypes.ECO_POINTS:
            qualifies = student.student_profile.eco_points >= badge.criteria_value

        if qualifies:
            _, created = UserBadge.objects.get_or_create(user=student, badge=badge)
            if created:
                awarded_badges.append(badge)

    return awarded_badges

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from gamification.models import PointTransaction
from gamification.services import award_points, evaluate_badges, refresh_profile_totals

from .models import ActivityCompletion, ActivitySubmission, DailyActivity


def is_admin_allowed_for_student(admin_user, student_user):
    admin_profile = getattr(admin_user, "admin_profile", None)
    if not admin_profile or admin_profile.institution_id is None:
        return True
    student_profile = getattr(student_user, "student_profile", None)
    return bool(student_profile and student_profile.institution_id == admin_profile.institution_id)


def resolve_activity_source(activity, submission_date):
    if DailyActivity.objects.filter(activity=activity, date=submission_date).exists():
        return ActivityCompletion.SourceTypes.DAILY_ACTIVITY
    return ActivityCompletion.SourceTypes.ACTIVITY


@transaction.atomic
def submit_activity(student, activity, *, description="", proof_image=None):
    submission_date = timezone.localdate()
    if not activity.is_active:
        raise serializers.ValidationError({"activity": ["This activity is not active."]})

    duplicate_submission = ActivitySubmission.objects.filter(
        student=student,
        activity=activity,
        submission_date=submission_date,
    ).exclude(status=ActivitySubmission.Statuses.REJECTED)
    if duplicate_submission.exists():
        raise serializers.ValidationError(
            {"activity": ["You have already completed this activity today."]}
        )

    if activity.requires_proof and not proof_image:
        raise serializers.ValidationError({"proof_image": ["A proof image is required for this activity."]})

    status = ActivitySubmission.Statuses.PENDING if activity.requires_proof else ActivitySubmission.Statuses.APPROVED
    source = resolve_activity_source(activity, submission_date)

    submission = ActivitySubmission.objects.create(
        student=student,
        activity=activity,
        proof_image=proof_image,
        description=description,
        status=status,
        submission_date=submission_date,
        verified_at=timezone.now() if status == ActivitySubmission.Statuses.APPROVED else None,
    )

    if status == ActivitySubmission.Statuses.APPROVED:
        ActivityCompletion.objects.get_or_create(
            student=student,
            activity=activity,
            campaign=None,
            date=submission_date,
            defaults={
                "points_earned": activity.eco_points,
                "source": source,
            },
        )
        award_points(
            student,
            activity.eco_points,
            PointTransaction.SourceTypes.ACTIVITY,
            f"activity-submission:{submission.id}",
            {"activity_id": activity.id, "submission_date": submission_date.isoformat()},
        )
        evaluate_badges(student)
    else:
        refresh_profile_totals(student)

    return submission


@transaction.atomic
def review_activity_submission(submission, reviewer, *, approve, rejection_reason=""):
    if submission.status != ActivitySubmission.Statuses.PENDING:
        raise serializers.ValidationError({"submission": ["Only pending submissions can be reviewed."]})

    if not is_admin_allowed_for_student(reviewer, submission.student):
        raise serializers.ValidationError({"submission": ["You cannot review this student's submission."]})

    submission.verified_by = reviewer
    submission.verified_at = timezone.now()
    submission.rejection_reason = rejection_reason

    if approve:
        submission.status = ActivitySubmission.Statuses.APPROVED
        submission.save(update_fields=["status", "verified_by", "verified_at", "rejection_reason"])
        source = resolve_activity_source(submission.activity, submission.submission_date)
        ActivityCompletion.objects.get_or_create(
            student=submission.student,
            activity=submission.activity,
            campaign=None,
            date=submission.submission_date,
            defaults={
                "points_earned": submission.activity.eco_points,
                "source": source,
            },
        )
        award_points(
            submission.student,
            submission.activity.eco_points,
            PointTransaction.SourceTypes.ACTIVITY,
            f"activity-submission:{submission.id}",
            {"activity_id": submission.activity_id, "submission_date": submission.submission_date.isoformat()},
        )
        evaluate_badges(submission.student)
    else:
        submission.status = ActivitySubmission.Statuses.REJECTED
        submission.save(update_fields=["status", "verified_by", "verified_at", "rejection_reason"])
        refresh_profile_totals(submission.student)

    return submission

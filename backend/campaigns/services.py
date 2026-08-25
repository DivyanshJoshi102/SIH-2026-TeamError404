from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from activities.models import ActivityCompletion
from activities.services import is_admin_allowed_for_student
from gamification.models import PointTransaction
from gamification.services import award_points, evaluate_badges, refresh_profile_totals

from .models import CampaignSubmission


@transaction.atomic
def submit_campaign(student, campaign, *, description="", proof_image=None):
    today = timezone.localdate()
    if not campaign.is_active or campaign.start_date > today or campaign.end_date < today:
        raise serializers.ValidationError({"campaign": ["This campaign is not currently active."]})

    duplicate = CampaignSubmission.objects.filter(
        student=student,
        campaign=campaign,
    ).exclude(status=CampaignSubmission.Statuses.REJECTED)
    if duplicate.exists():
        raise serializers.ValidationError({"campaign": ["You have already joined this campaign."]})

    if campaign.requires_proof and not proof_image:
        raise serializers.ValidationError({"proof_image": ["A proof image is required for this campaign."]})

    submission = CampaignSubmission.objects.create(
        student=student,
        campaign=campaign,
        proof_image=proof_image,
        description=description,
    )
    refresh_profile_totals(student)
    return submission


@transaction.atomic
def review_campaign_submission(submission, reviewer, *, approve, rejection_reason="", is_featured=False):
    if submission.status != CampaignSubmission.Statuses.PENDING:
        raise serializers.ValidationError({"submission": ["Only pending submissions can be reviewed."]})

    if not is_admin_allowed_for_student(reviewer, submission.student):
        raise serializers.ValidationError({"submission": ["You cannot review this student's campaign submission."]})

    submission.verified_by = reviewer
    submission.verified_at = timezone.now()
    submission.rejection_reason = rejection_reason

    if approve:
        submission.status = CampaignSubmission.Statuses.APPROVED
        submission.is_featured = is_featured
        submission.save(update_fields=["status", "verified_by", "verified_at", "rejection_reason", "is_featured"])
        ActivityCompletion.objects.get_or_create(
            student=submission.student,
            activity=None,
            campaign=submission.campaign,
            date=submission.submission_date,
            defaults={
                "points_earned": submission.campaign.eco_points,
                "source": ActivityCompletion.SourceTypes.CAMPAIGN,
            },
        )
        award_points(
            submission.student,
            submission.campaign.eco_points,
            PointTransaction.SourceTypes.CAMPAIGN,
            f"campaign-submission:{submission.id}",
            {"campaign_id": submission.campaign_id},
        )
        evaluate_badges(submission.student)
    else:
        submission.status = CampaignSubmission.Statuses.REJECTED
        submission.is_featured = False
        submission.save(update_fields=["status", "verified_by", "verified_at", "rejection_reason", "is_featured"])
        refresh_profile_totals(submission.student)

    return submission

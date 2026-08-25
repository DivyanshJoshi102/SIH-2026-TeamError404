from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from activities.models import ActivityCompletion, ActivitySubmission
from campaigns.models import Campaign, CampaignSubmission
from gamification.models import PointTransaction, UserBadge
from institutions.models import Institution
from quizzes.models import QuizAttempt
from users.models import StudentProfile


def get_student_dashboard(student):
    today = timezone.localdate()
    thirty_days_ago = today - timedelta(days=29)
    heatmap_counts = {
        item["date"].isoformat(): item["count"]
        for item in ActivityCompletion.objects.filter(student=student, date__gte=thirty_days_ago)
        .values("date")
        .annotate(count=Count("id"))
    }
    heatmap = []
    current_day = thirty_days_ago
    while current_day <= today:
        heatmap.append({
            "date": current_day.isoformat(),
            "count": heatmap_counts.get(current_day.isoformat(), 0),
        })
        current_day += timedelta(days=1)

    return {
        "student": {
            "name": student.full_name,
            "email": student.email,
            "eco_points": student.student_profile.eco_points,
            "current_streak": student.student_profile.current_streak,
            "longest_streak": student.student_profile.longest_streak,
            "total_activities": student.student_profile.total_activities,
            "institution": student.student_profile.institution.name,
            "state": student.student_profile.institution.location.state,
            "district": student.student_profile.institution.location.district,
        },
        "recent_activity_submissions": [
            {
                "id": submission.id,
                "title": submission.activity.title,
                "status": submission.status,
                "submitted_at": submission.submitted_at,
            }
            for submission in ActivitySubmission.objects.filter(student=student).select_related("activity")[:5]
        ],
        "recent_campaign_submissions": [
            {
                "id": submission.id,
                "title": submission.campaign.title,
                "status": submission.status,
                "submitted_at": submission.submitted_at,
            }
            for submission in CampaignSubmission.objects.filter(student=student).select_related("campaign")[:5]
        ],
        "recent_quizzes": [
            {
                "id": attempt.id,
                "title": attempt.quiz.title,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "earned_points": attempt.earned_points,
                "submitted_at": attempt.submitted_at,
            }
            for attempt in QuizAttempt.objects.filter(student=student).select_related("quiz")[:5]
        ],
        "badges": [
            {
                "id": badge.badge_id,
                "name": badge.badge.name,
                "description": badge.badge.description,
                "icon": badge.badge.icon,
                "awarded_at": badge.awarded_at,
            }
            for badge in UserBadge.objects.filter(user=student).select_related("badge")
        ],
        "heatmap": heatmap,
    }


def scoped_student_profiles(user, scope):
    queryset = StudentProfile.objects.select_related("user", "institution__location")
    if scope == "global":
        return queryset

    if user.role == "STUDENT":
        institution = user.student_profile.institution
    else:
        institution = user.admin_profile.institution
        if institution is None:
            return queryset

    if scope == "institution":
        return queryset.filter(institution=institution)
    if scope == "district":
        return queryset.filter(institution__location__district=institution.location.district)
    if scope == "state":
        return queryset.filter(institution__location__state=institution.location.state)
    return queryset


def period_filter(period):
    today = timezone.localdate()
    if period == "daily":
        return Q(user__point_transactions__created_at__date=today)
    if period == "weekly":
        return Q(user__point_transactions__created_at__date__gte=today - timedelta(days=6))
    if period == "monthly":
        return Q(user__point_transactions__created_at__date__gte=today - timedelta(days=29))
    return Q()


def get_leaderboard(user, scope, period):
    profiles = scoped_student_profiles(user, scope)
    if period == "all_time":
        profiles = profiles.annotate(total_points=Coalesce(Sum("user__point_transactions__points"), 0))
    else:
        profiles = profiles.annotate(
            total_points=Coalesce(
                Sum("user__point_transactions__points", filter=period_filter(period)),
                0,
            )
        )
    profiles = profiles.order_by("-total_points", "-current_streak", "user__full_name")[:20]

    return [
        {
            "rank": index,
            "student_id": profile.user_id,
            "name": profile.user.full_name,
            "institution": profile.institution.name,
            "state": profile.institution.location.state,
            "district": profile.institution.location.district,
            "eco_points": profile.total_points,
            "current_streak": profile.current_streak,
        }
        for index, profile in enumerate(profiles, start=1)
    ]


def get_admin_dashboard(admin_user):
    institution = admin_user.admin_profile.institution
    student_filter = Q()
    submission_filter = Q()
    campaign_submission_filter = Q()

    if institution is not None:
        student_filter = Q(institution=institution)
        submission_filter = Q(student__student_profile__institution=institution)
        campaign_submission_filter = Q(student__student_profile__institution=institution)

    return {
        "student_count": StudentProfile.objects.filter(student_filter).count(),
        "institution_count": Institution.objects.count() if institution is None else 1,
        "pending_activity_submissions": ActivitySubmission.objects.filter(submission_filter, status=ActivitySubmission.Statuses.PENDING).count(),
        "approved_activity_submissions": ActivitySubmission.objects.filter(submission_filter, status=ActivitySubmission.Statuses.APPROVED).count(),
        "pending_campaign_submissions": CampaignSubmission.objects.filter(campaign_submission_filter, status=CampaignSubmission.Statuses.PENDING).count(),
        "approved_campaign_submissions": CampaignSubmission.objects.filter(campaign_submission_filter, status=CampaignSubmission.Statuses.APPROVED).count(),
        "active_campaigns": Campaign.objects.filter(is_active=True).count(),
        "total_points_awarded": PointTransaction.objects.filter(
            Q(student__student_profile__institution=institution) if institution else Q()
        ).aggregate(total=Coalesce(Sum("points"), 0))["total"],
    }

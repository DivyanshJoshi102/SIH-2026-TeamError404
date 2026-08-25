from PIL import Image
from rest_framework import serializers

from .models import Activity, ActivityCompletion, ActivitySubmission, DailyActivity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = (
            "id",
            "title",
            "description",
            "category",
            "difficulty",
            "eco_points",
            "requires_proof",
            "is_active",
        )


class ActivitySubmissionSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = ActivitySubmission
        fields = (
            "id",
            "activity",
            "student_name",
            "description",
            "proof_image",
            "status",
            "submission_date",
            "submitted_at",
            "verified_at",
            "rejection_reason",
        )


class ActivitySubmissionCreateSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True)
    proof_image = serializers.ImageField(required=False, allow_null=True)

    def validate_proof_image(self, value):
        if value is None:
            return value
        try:
            image = Image.open(value)
            image.verify()
            value.seek(0)
        except Exception as exc:
            raise serializers.ValidationError("Upload a valid image file.") from exc
        return value


class ActivitySubmissionReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=(("APPROVE", "Approve"), ("REJECT", "Reject")))
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["action"] == "REJECT" and not attrs.get("rejection_reason"):
            raise serializers.ValidationError({"rejection_reason": ["Provide a rejection reason."]})
        return attrs


class DailyActivitySerializer(serializers.Serializer):
    activity = ActivitySerializer()
    date = serializers.DateField()
    completed = serializers.BooleanField()


class ActivityCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCompletion
        fields = ("date", "points_earned", "source")

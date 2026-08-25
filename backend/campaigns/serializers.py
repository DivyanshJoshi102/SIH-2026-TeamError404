from PIL import Image
from rest_framework import serializers

from .models import Campaign, CampaignSubmission


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = (
            "id",
            "title",
            "description",
            "eco_points",
            "start_date",
            "end_date",
            "requires_proof",
            "is_active",
        )


class CampaignSubmissionSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = CampaignSubmission
        fields = (
            "id",
            "campaign",
            "student_name",
            "description",
            "proof_image",
            "status",
            "submission_date",
            "submitted_at",
            "verified_at",
            "rejection_reason",
            "is_featured",
        )


class CampaignSubmissionCreateSerializer(serializers.Serializer):
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


class CampaignSubmissionReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=(("APPROVE", "Approve"), ("REJECT", "Reject")))
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    is_featured = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if attrs["action"] == "REJECT" and not attrs.get("rejection_reason"):
            raise serializers.ValidationError({"rejection_reason": ["Provide a rejection reason."]})
        return attrs

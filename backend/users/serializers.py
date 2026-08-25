from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from gamification.models import UserBadge
from institutions.models import Institution

from .models import AdminProfile, StudentProfile, User


def generate_unique_username(email):
    base_username = slugify(email.split("@", 1)[0]) or "user"
    candidate = base_username
    counter = 1
    while User.objects.filter(username=candidate).exists():
        counter += 1
        candidate = f"{base_username}{counter}"
    return candidate


class InstitutionSummarySerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="location.state", read_only=True)
    district = serializers.CharField(source="location.district", read_only=True)

    class Meta:
        model = Institution
        fields = ("id", "name", "type", "state", "district")


class UserBadgeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="badge.id", read_only=True)
    name = serializers.CharField(source="badge.name", read_only=True)
    description = serializers.CharField(source="badge.description", read_only=True)
    icon = serializers.CharField(source="badge.icon", read_only=True)
    awarded_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserBadge
        fields = ("id", "name", "description", "icon", "awarded_at")


class StudentProfileSerializer(serializers.ModelSerializer):
    institution = InstitutionSummarySerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            "institution",
            "eco_points",
            "current_streak",
            "longest_streak",
            "total_activities",
        )


class AdminProfileSerializer(serializers.ModelSerializer):
    institution = InstitutionSummarySerializer(read_only=True)

    class Meta:
        model = AdminProfile
        fields = ("admin_type", "institution")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "full_name", "role")


class ProfileSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    admin_profile = AdminProfileSerializer(read_only=True)
    badges = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "full_name",
            "role",
            "student_profile",
            "admin_profile",
            "badges",
        )

    def get_badges(self, obj):
        return UserBadgeSerializer(obj.user_badges.select_related("badge").all(), many=True).data


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(choices=User.Roles.choices)
    institution_id = serializers.IntegerField(required=False)
    admin_type = serializers.ChoiceField(choices=AdminProfile.AdminTypes.choices, required=False)

    def validate(self, attrs):
        role = attrs["role"]
        institution_id = attrs.get("institution_id")
        admin_type = attrs.get("admin_type")

        if role == User.Roles.STUDENT and not institution_id:
            raise serializers.ValidationError({"institution_id": ["Institution is required for students."]})

        if role == User.Roles.ADMIN and not admin_type:
            raise serializers.ValidationError({"admin_type": ["Admin type is required for admin users."]})

        if institution_id:
            attrs["institution"] = Institution.objects.filter(pk=institution_id, is_active=True).first()
            if not attrs["institution"]:
                raise serializers.ValidationError({"institution_id": ["Institution not found."]})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        institution = validated_data.pop("institution", None)
        validated_data.pop("institution_id", None)
        admin_type = validated_data.pop("admin_type", None)
        password = validated_data.pop("password")

        user = User.objects.create(
            username=generate_unique_username(validated_data["email"]),
            **validated_data,
        )
        user.set_password(password)
        user.save(update_fields=["password"])

        if user.role == User.Roles.STUDENT:
            StudentProfile.objects.create(user=user, institution=institution)
        else:
            AdminProfile.objects.create(
                user=user,
                admin_type=admin_type,
                institution=institution if admin_type in {
                    AdminProfile.AdminTypes.TEACHER,
                    AdminProfile.AdminTypes.ECO_CLUB,
                } else None,
            )

        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = User.objects.filter(email__iexact=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is inactive."})

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": ProfileSerializer(user).data,
        }

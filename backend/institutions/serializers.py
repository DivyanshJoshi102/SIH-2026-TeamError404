from rest_framework import serializers

from .models import Institution, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id", "state", "district")


class InstitutionSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="location.state", read_only=True)
    district = serializers.CharField(source="location.district", read_only=True)

    class Meta:
        model = Institution
        fields = ("id", "name", "type", "state", "district", "is_active")

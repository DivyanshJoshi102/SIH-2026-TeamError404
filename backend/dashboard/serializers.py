from rest_framework import serializers


class LeaderboardQuerySerializer(serializers.Serializer):
    scope = serializers.ChoiceField(choices=("global", "institution", "district", "state"), default="global", required=False)
    period = serializers.ChoiceField(choices=("all_time", "daily", "weekly", "monthly"), default="all_time", required=False)

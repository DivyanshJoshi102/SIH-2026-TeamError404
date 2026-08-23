from rest_framework import serializers
from .models import Submission, Mission

class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')
    mission_title = serializers.ReadOnlyField(source='mission.title')

    class Meta:
        model = Submission
        fields = ['id', 'student_name', 'mission_title', 'is_approved']
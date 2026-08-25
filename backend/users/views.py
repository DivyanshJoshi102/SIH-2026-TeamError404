from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.api import success_response

from .serializers import EmailTokenObtainPairSerializer, ProfileSerializer, RegistrationSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(ProfileSerializer(user).data, message="Registration successful.", status=status.HTTP_201_CREATED)


class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class ProfileView(APIView):
    def get(self, request):
        return success_response(ProfileSerializer(request.user).data)


class EmailTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

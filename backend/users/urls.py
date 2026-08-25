from django.urls import path

from .views import EmailTokenObtainPairView, EmailTokenRefreshView, ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", EmailTokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
]

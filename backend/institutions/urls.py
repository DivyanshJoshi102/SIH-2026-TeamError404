from django.urls import path

from .views import InstitutionListView, LocationListView

urlpatterns = [
    path("locations/", LocationListView.as_view(), name="location-list"),
    path("", InstitutionListView.as_view(), name="institution-list"),
]

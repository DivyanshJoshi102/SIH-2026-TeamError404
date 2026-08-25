from rest_framework import generics, permissions

from .models import Institution, Location
from .serializers import InstitutionSerializer, LocationSerializer


class LocationListView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Location.objects.all()


class InstitutionListView(generics.ListAPIView):
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Institution.objects.filter(is_active=True).select_related("location")
        state = self.request.query_params.get("state")
        district = self.request.query_params.get("district")
        institution_type = self.request.query_params.get("type")

        if state:
            queryset = queryset.filter(location__state__iexact=state)
        if district:
            queryset = queryset.filter(location__district__iexact=district)
        if institution_type:
            queryset = queryset.filter(type=institution_type)
        return queryset

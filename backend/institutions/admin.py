from django.contrib import admin

from .models import Institution, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("state", "district")
    search_fields = ("state", "district")


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "location", "is_active")
    list_filter = ("type", "is_active", "location__state", "location__district")
    search_fields = ("name", "location__state", "location__district")

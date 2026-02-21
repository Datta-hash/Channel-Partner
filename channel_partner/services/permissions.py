# services/permissions.py
from rest_framework.permissions import BasePermission
from User.models import AdminProfile

class IsAdminProfile(BasePermission):
    message = "You do not have the authorization."

    def has_permission(self, request, view):
        return AdminProfile.objects.filter(user=request.user).exists()
    

from rest_framework.permissions import BasePermission
from django.conf import settings

class IsValidAPIKey(BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get("X-API-KEY")
        return api_key == settings.INTER_SERVICE_API_KEY
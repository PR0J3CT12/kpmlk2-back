from rest_framework import permissions
from kpm.apps.users.models import User


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return False
        return True


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            if request.user:
                if user.is_admin:
                    return True
            return False
        except Exception:
            return False
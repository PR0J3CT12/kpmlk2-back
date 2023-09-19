from rest_framework import permissions
from kpm.apps.users.models import User, Admin


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


class IsTierZero(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            tier = Admin.objects.get(user=user).tier
            if tier == 0:
                return True
            return False
        except Exception:
            return False


class IsTierOne(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            tier = Admin.objects.get(user=user).tier
            if tier in [0, 1]:
                return True
            return False
        except Exception:
            return False


class IsTierTwo(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(id=request.user.id)
            tier = Admin.objects.get(user=user).tier
            if tier in [0, 1, 2]:
                return True
            return False
        except Exception:
            return False
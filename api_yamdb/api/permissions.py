from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_admin
            or request.user.is_staff
            or request.user.is_superuser
        )


class AdminOrReadOnly(permissions.BasePermission):
    """Админ, либо просто читает."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return bool(request.user.is_staff or request.user.is_admin)


class IsAuthorOrHasRightsOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_staff
        ):
            return True

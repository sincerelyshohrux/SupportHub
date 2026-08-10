from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Faqat admin rolidagi foydalanuvchilarga ruxsat beradi."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsAdminOrReadOnly(BasePermission):
    """
    O'qish (GET) — barcha autentifikatsiyadan o'tgan foydalanuvchilarga.
    Yozish (POST/PATCH/DELETE) — faqat admin'ga.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'admin'
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



class IsTicketOwnerOrAssigned(BasePermission):
    """
    - Admin: barcha ticketlarni ko'ra/o'zgartira oladi
    - Operator: faqat o'ziga biriktirilgan ticketni
    - Client: faqat o'zi yaratgan ticketni
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'operator':
            return obj.operator_id == user.id
        return obj.client_id == user.id
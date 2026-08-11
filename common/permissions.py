from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Faqat admin rolidagi foydalanuvchilarga ruxsat beradi."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsOperator(BasePermission):
    """Faqat operator rolidagi foydalanuvchilarga ruxsat beradi."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'operator'
        )


class IsTicketOwner(BasePermission):
    """Ticket faqat o'sha ticketni yaratgan client'ga tegishli bo'lsa ruxsat beradi."""

    def has_object_permission(self, request, view, obj):
        return obj.client_id == request.user.id


class IsAdminOrAssignedOperator(BasePermission):
    """
    Admin — har doim ruxsat.
    Operator — faqat o'ziga biriktirilgan ticket bo'lsa ruxsat.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'operator')
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.operator_id == request.user.id


class IsAdminOrReadOnly(BasePermission):
    """
    O'qish (GET) — barcha autentifikatsiyadan o'tgan foydalanuvchilarga.
    Yozish (POST/PATCH/DELETE) — faqat admin'ga. (Category uchun ishlatiladi)
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'admin'
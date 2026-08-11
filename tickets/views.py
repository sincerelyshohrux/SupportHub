from django.utils import timezone
from rest_framework import permissions, viewsets

from common.permissions import IsAdminOrReadOnly, IsTicketOwnerOrAssigned

from .models import Category, Ticket, TicketHistory
from .serializers import CategorySerializer, TicketSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/categories/
    POST   /api/categories/
    GET    /api/categories/{id}/
    PATCH  /api/categories/{id}/
    DELETE /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]



class TicketViewSet(viewsets.ModelViewSet):
    """
    GET    /api/tickets/
    POST   /api/tickets/
    GET    /api/tickets/{id}/
    PATCH  /api/tickets/{id}/
    DELETE /api/tickets/{id}/
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsTicketOwnerOrAssigned]

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related('client', 'operator', 'category')

        if user.role == 'admin':
            return qs
        if user.role == 'operator':
            return qs.filter(operator=user)
        return qs.filter(client=user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def perform_update(self, serializer):
        old_status = self.get_object().status
        ticket = serializer.save()

        if ticket.status != old_status:
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=self.request.user,
                old_status=old_status,
                new_status=ticket.status,
            )
            if ticket.status == Ticket.Status.RESOLVED and not ticket.resolved_at:
                ticket.resolved_at = timezone.now()
                ticket.save(update_fields=['resolved_at'])
from django.utils import timezone
from rest_framework import permissions, viewsets
from .tasks import notify_urgent_ticket
from .filters import TicketFilter
from common.permissions import (
    IsAdminOrAssignedOperator,
    IsAdminOrReadOnly,
    IsTicketOwner,
)

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
    permission_classes = [
        permissions.IsAuthenticated,
        IsTicketOwner | IsAdminOrAssignedOperator,
    ]

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related('client', 'operator', 'category')

        if user.role == 'admin':
            return qs
        if user.role == 'operator':
            return qs.filter(operator=user)
        return qs.filter(client=user)

    def perform_create(self, serializer):
        ticket = serializer.save(client=self.request.user)
        if ticket.priority == Ticket.Priority.URGENT:
            notify_urgent_ticket.delay(ticket.id)

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


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTicketOwner | IsAdminOrAssignedOperator,
    ]
    filterset_class = TicketFilter
    search_fields = ('title', 'description')
    ordering_fields = ('created_at', 'updated_at', 'priority', 'status')
    ordering = ('-created_at',)

    def get_queryset(self):
        ...



from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from common.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([IsAdmin])
def ticket_stats(request):
    """
    GET /api/tickets/stats/
    Statistika 5 daqiqaga cache qilinadi.
    """
    stats = cache.get('ticket_stats')

    if stats is None:
        stats = {
            'total': Ticket.objects.count(),
            'new': Ticket.objects.filter(status=Ticket.Status.NEW).count(),
            'in_progress': Ticket.objects.filter(status=Ticket.Status.IN_PROGRESS).count(),
            'resolved': Ticket.objects.filter(status=Ticket.Status.RESOLVED).count(),
            'closed': Ticket.objects.filter(status=Ticket.Status.CLOSED).count(),
            'urgent': Ticket.objects.filter(priority=Ticket.Priority.URGENT).count(),
            'cached': False,
        }
        cache.set('ticket_stats', stats, timeout=300)  # 5 daqiqa
    else:
        stats = dict(stats)
        stats['cached'] = True

    return Response(stats)
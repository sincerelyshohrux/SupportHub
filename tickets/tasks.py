import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('request_logger')


@shared_task
def notify_urgent_ticket(ticket_id):
    """Urgent ticket yaratilganda bildirishnoma yuboradi (hozircha logga yozish)."""
    from .models import Ticket

    try:
        ticket = Ticket.objects.select_related('client', 'category').get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return

    logger.info(
        'URGENT TICKET BILDIRISHNOMASI: #%s - %s (mijoz: %s)',
        ticket.id, ticket.title, ticket.client.username,
    )



@shared_task
def check_stale_tickets():
    """24 soatdan ortiq 'new' holatda turgan ticketlarni tekshiradi (kunlik)."""
    from .models import Ticket

    threshold = timezone.now() - timedelta(hours=24)
    stale_tickets = Ticket.objects.filter(status=Ticket.Status.NEW, created_at__lt=threshold)

    count = stale_tickets.count()
    for ticket in stale_tickets:
        logger.warning(
            'ESKIRGAN TICKET: #%s - %s (%s dan beri "new" holatda)',
            ticket.id, ticket.title, ticket.created_at,
        )

    return f'{count} ta eskirgan ticket topildi'
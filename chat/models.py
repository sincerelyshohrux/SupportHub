from django.conf import settings
from django.db import models


class Message(models.Model):
    """Ticket ichidagi yozishma (chat) xabari. WebSocket orqali real vaqtda yuboriladi."""

    ticket = models.ForeignKey(
        'tickets.Ticket',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Qaysi murojaatga tegishli',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Xabar yuboruvchi',
    )
    text = models.TextField('Xabar matni')
    is_read = models.BooleanField("Xabar o'qilganmi", default=False)
    created_at = models.DateTimeField('Yuborilgan vaqt', auto_now_add=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} -> Ticket #{self.ticket_id}'

from django.conf import settings
from django.db import models


class Category(models.Model):
    """Murojaat kategoriyasi (masalan: Texnik muammo, To'lov muammosi)."""

    name = models.CharField('Kategoriya nomi', max_length=100, unique=True)
    description = models.TextField('Kategoriya izohi', blank=True)
    is_active = models.BooleanField('Faol yoki faol emas', default=True)
    created_at = models.DateTimeField('Yaratilgan vaqt', auto_now_add=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Mijoz tomonidan yuborilgan murojaat."""

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    title = models.CharField('Murojaat sarlavhasi', max_length=255)
    description = models.TextField('Muammo tavsifi')
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_tickets',
        verbose_name='Murojaat yuborgan mijoz',
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='operator_tickets',
        verbose_name='Biriktirilgan operator',
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='tickets',
        verbose_name='Murojaat kategoriyasi',
        null=True,
        blank=True,
    )
    status = models.CharField(
        'Holat', max_length=20, choices=Status.choices, default=Status.NEW,
    )
    priority = models.CharField(
        'Muhimlik darajasi', max_length=20, choices=Priority.choices, default=Priority.MEDIUM,
    )
    created_at = models.DateTimeField('Yaratilgan vaqt', auto_now_add=True)
    updated_at = models.DateTimeField('Oxirgi yangilangan vaqt', auto_now=True)
    resolved_at = models.DateTimeField('Yopilgan vaqt', null=True, blank=True)

    class Meta:
        verbose_name = 'Murojaat'
        verbose_name_plural = 'Murojaatlar'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} - {self.title}'


class TicketHistory(models.Model):
    """Ticket holati o'zgarishlarining tarixi."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Murojaat',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='ticket_changes',
        verbose_name="O'zgarishni amalga oshirgan shaxs",
        null=True,
    )
    old_status = models.CharField('Avvalgi holat', max_length=20, blank=True)
    new_status = models.CharField('Yangi holat', max_length=20, blank=True)
    created_at = models.DateTimeField("O'zgartirilgan vaqt", auto_now_add=True)

    class Meta:
        verbose_name = 'Murojaat tarixi'
        verbose_name_plural = 'Murojaat tarixlari'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ticket #{self.ticket_id}: {self.old_status} -> {self.new_status}'

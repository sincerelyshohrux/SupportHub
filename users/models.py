from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Tizim foydalanuvchisi. Django'ning standart AbstractUser modelidan
    meros olib, qo'shimcha maydonlar bilan kengaytirilgan.
    """

    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        OPERATOR = 'operator', 'Operator'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField('Elektron pochta', unique=True)
    role = models.CharField(
        'Rol',
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    phone = models.CharField('Telefon raqami', max_length=20, blank=True)
    created_at = models.DateTimeField("Ro'yxatdan o'tgan vaqt", auto_now_add=True)

    def __str__(self):
        return f'{self.username} ({self.role})'

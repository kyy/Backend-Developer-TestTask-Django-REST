from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидание'
        PROCESSING = 'processing', 'В обработке'
        COMPLETED = 'completed', 'Выплачено'
        FAILED = 'failed', 'Ошибка'
        CANCELLED = 'cancelled', 'Отменено'

    class Currency(models.TextChoices):
        RUB = 'RUB', 'Российский рубль'
        USD = 'USD', 'Доллар США'
        EUR = 'EUR', 'Евро'
        KZT = 'KZT', 'Казахстанский тенге'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Идентификатор'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма выплаты'
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUB,
        verbose_name='Валюта'
    )

    recipient_details = models.JSONField(
        verbose_name='Реквизиты получателя'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус заявки'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание/Комментарий'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заявка на выплату'
        verbose_name_plural = 'Заявки на выплату'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Выплата {self.id} - {self.amount} {self.currency}"
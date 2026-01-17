from decimal import Decimal
from ninja import Schema, Field, ModelSchema
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pydantic import UUID4, field_validator, computed_field, model_validator, BaseModel
from .models import Currency, Status, Payout


class CardSchema(Schema):
    card_number: str  = Field(
        ...,
        min_length=13,
        max_length=19,
        examples=[5555555555554444, 6011000990139424, 5892830000000000],
        description="Номер карты",
        pattern = r'^[0-9]{13,19}$',
    )
    card_holder: str = Field(
        ...,
        min_length=4,
        max_length=100,
        examples=["Ivanov Ivan"],
        description="Держатель карты",
        pattern=r'^[A-ZА-ЯЁ][a-zа-яё]+(-[A-ZА-ЯЁ][a-zа-яё]+)? [A-ZА-ЯЁ][a-zа-яё]+(-[A-ZА-ЯЁ][a-zа-яё]+)?$',

    )
    expiry_date: str = Field(
        ...,
        pattern=r'^(0[1-9]|1[0-2])\/([0-9]{2})$',
        description="Срок действия в формате ММ/ГГ",
        examples=["12/25"]
    )

    @field_validator('card_number')
    def validate_luhn_algorithm(cls, v):
        """Проверка номера карты по алгоритму Луна"""
        # Удаляем все нецифровые символы
        digits = [int(d) for d in v if d.isdigit()]

        if len(digits) < 13 or len(digits) > 19:
            raise ValueError('Номер карты должен содержать от 13 до 19 цифр')

        # Алгоритм Луна
        check_digit = digits.pop()
        digits.reverse()

        total = 0
        for i, digit in enumerate(digits):
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit

        total += check_digit

        if total % 10 != 0:
            raise ValueError('Неверный номер карты')

        return v

class PayoutTimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class PayoutIdentifierMixin(Schema):
    id: UUID4

class PayoutStatusMixin(Schema):
    status: Optional[Status] = Field(None, description="Статус заявки")

class PayoutDescriptionMixin(Schema):
    description: Optional[str] = Field(None, max_length=500, description="Описание")

class PayoutDetailsMixin(Schema):
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12 ,description="Сумма выплаты (должна быть больше 0)")
    currency: Currency = Field(..., description="Валюта выплаты")
    recipient_details: CardSchema = Field(..., description="Данные получателя")


class PayoutCreateSchema(
    PayoutDescriptionMixin,
    PayoutDetailsMixin
):
    pass

class PayoutUpdateSchema(
    PayoutStatusMixin,
    PayoutDescriptionMixin
):

    class Config:
        schema_extra = {
            "example": {
                "status": "processing",
                "description": "Обновленный комментарий"
            }
        }


class PayoutResponseSchema(
    PayoutTimestampMixin,
    PayoutStatusMixin,
    PayoutDescriptionMixin,
    PayoutIdentifierMixin,
    PayoutDetailsMixin
):
    pass


class ErrorSchema(Schema):
    detail: str
    code: Optional[str] = None
    field: Optional[str] = None


class ValidationErrorSchema(Schema):
    detail: list[Dict[str, Any]]

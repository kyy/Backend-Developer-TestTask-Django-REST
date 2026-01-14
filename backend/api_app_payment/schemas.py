from ninja import Schema, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums для валидации
class CurrencyEnum(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    KZT = "KZT"


class StatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Базовые схемы для валидации реквизитов
class BankAccountSchema(Schema):
    account_number: str = Field(..., min_length=10, max_length=34)
    bank_name: str = Field(..., min_length=2, max_length=100)
    bik: Optional[str] = Field(None, min_length=9, max_length=9)
    correspondent_account: Optional[str] = Field(None, min_length=20, max_length=20)


class CardSchema(Schema):
    card_number: str = Field(..., min_length=16, max_length=19)
    card_holder: str = Field(..., min_length=2, max_length=100)
    expiry_date: str = Field(..., pattern=r'^(0[1-9]|1[0-2])\/([0-9]{2})$')


class CryptoWalletSchema(Schema):
    wallet_address: str = Field(..., min_length=26, max_length=64)
    network: str = Field(..., min_length=2, max_length=20)
    currency: str = Field(..., min_length=2, max_length=10)


# Схемы для API
class PayoutBaseSchema(Schema):
    amount: float = Field(..., gt=0, description="Сумма выплаты")
    currency: CurrencyEnum = Field(CurrencyEnum.RUB, description="Валюта выплаты")
    recipient_details: Dict[str, Any] = Field(..., description="Реквизиты получателя")
    description: Optional[str] = Field(None, max_length=500, description="Описание")


class PayoutCreateSchema(PayoutBaseSchema):
    class Config:
        schema_extra = {
            "example": {
                "amount": 1000.50,
                "currency": "RUB",
                "description": "Выплата за услуги",
                "recipient_details": {
                    "type": "bank_account",
                    "account_number": "40702810500000012345",
                    "bank_name": "Альфа-Банк",
                    "bik": "044525593",
                    "correspondent_account": "30101810200000000593"
                }
            }
        }


class PayoutUpdateSchema(Schema):
    status: Optional[StatusEnum] = Field(None, description="Статус заявки")
    description: Optional[str] = Field(None, max_length=500, description="Описание")

    class Config:
        schema_extra = {
            "example": {
                "status": "processing",
                "description": "Обновленный комментарий"
            }
        }


class PayoutResponseSchema(Schema):
    id: str
    amount: float
    currency: str
    recipient_details: Dict[str, Any]
    status: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class PayoutListResponseSchema(Schema):
    items: list[PayoutResponseSchema]
    count: int
    page: Optional[int] = None
    total_pages: Optional[int] = None


class ErrorSchema(Schema):
    detail: str
    code: Optional[str] = None
    field: Optional[str] = None


class ValidationErrorSchema(Schema):
    detail: list[Dict[str, Any]]
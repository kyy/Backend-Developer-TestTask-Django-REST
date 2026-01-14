from typing import Dict, Any
from ninja.errors import ValidationError
from .schemas import BankAccountSchema, CardSchema, CryptoWalletSchema


class PayoutValidator:
    @staticmethod
    def validate_recipient_details(data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация реквизитов получателя"""
        details_type = data.get('type')

        if not details_type:
            raise ValidationError(
                [{"msg": "Поле 'type' обязательно для recipient_details", "field": "recipient_details.type"}])

        try:
            if details_type == 'bank_account':
                return BankAccountSchema(**data).dict()
            elif details_type == 'card':
                return CardSchema(**data).dict()
            elif details_type == 'crypto':
                return CryptoWalletSchema(**data).dict()
            else:
                raise ValidationError(
                    [{"msg": f"Неподдерживаемый тип реквизитов: {details_type}", "field": "recipient_details.type"}])
        except ValidationError as e:
            raise ValidationError(
                [{"msg": str(err), "field": f"recipient_details.{field}"} for field, err in e.errors.items()])

    @staticmethod
    def validate_amount_by_currency(amount: float, currency: str) -> None:
        """Валидация суммы в зависимости от валюты"""
        limits = {
            'RUB': {'min': 10, 'max': 1000000},
            'USD': {'min': 1, 'max': 10000},
            'EUR': {'min': 1, 'max': 10000},
            'KZT': {'min': 100, 'max': 5000000},
        }

        if currency not in limits:
            raise ValidationError([{"msg": f"Неподдерживаемая валюта: {currency}", "field": "currency"}])

        limit = limits[currency]
        if amount < limit['min']:
            raise ValidationError([{"msg": f"Минимальная сумма для {currency}: {limit['min']}", "field": "amount"}])
        if amount > limit['max']:
            raise ValidationError([{"msg": f"Максимальная сумма для {currency}: {limit['max']}", "field": "amount"}])
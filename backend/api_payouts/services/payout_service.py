from typing import List, Dict, Any
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja.pagination import paginate, PageNumberPagination

from ..models import Payout
from ..schemas import PayoutCreateSchema, PayoutUpdateSchema
from ..tasks import task_payout


class PayoutService:
    """Сервис для работы с выплатами"""

    @staticmethod
    @paginate(PageNumberPagination, page_size=15)
    def get_list_payouts() -> List[Payout]:
        """Получить все выплаты"""
        return Payout.objects.all().order_by('-created_at')

    @staticmethod
    def get_payout(payout_id: str) -> Payout:
        """Получить выплату по ID"""
        return get_object_or_404(Payout, id=payout_id)

    @staticmethod
    def create_payout(payload: PayoutCreateSchema) -> Payout:
        """Создать новую выплату"""
        payout = Payout.objects.create(**payload.dict(exclude_unset=True), status='pending')
        transaction.on_commit(lambda: task_payout.apply_async(args=[payout.id], countdown=3))
        return payout

    @staticmethod
    def delete_payout(payout_id: str) -> Dict[str, Any]:
        """Удалить выплату"""
        payout = get_object_or_404(Payout, id=payout_id)
        payout.delete()
        return {"success": True}

    @staticmethod
    def update_payout(payout_id: str, payload: PayoutUpdateSchema) -> Payout:
        """Обновить заявку - статус или комментарий"""
        payout = get_object_or_404(Payout, id=payout_id)

        for attr, value in payload.dict(exclude_unset=True).items():
            if hasattr(payout, attr):
                setattr(payout, attr, value)

        payout.save()
        return payout




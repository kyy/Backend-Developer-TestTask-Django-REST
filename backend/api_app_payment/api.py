from ninja import Router, Query, Schema
from ninja.pagination import paginate, PageNumberPagination
from django.shortcuts import get_object_or_404
from typing import List, Optional, Dict, Any
from django.db.models import Q
from datetime import datetime, timedelta

from pydantic import Field

from .models import Payout
from .schemas import (
    PayoutCreateSchema,
    PayoutUpdateSchema,
    PayoutResponseSchema,
    PayoutListResponseSchema,
    ErrorSchema,
    StatusEnum
)
from .validators import PayoutValidator

router = Router(tags=["Управление заявками на выплату средств"])


@router.get("/", response=List[PayoutResponseSchema])
def list_payouts(request):
    """Список всех заявок"""
    return Payout.objects.all().order_by('-created_at')


@router.get("/{payout_id}/", response=PayoutResponseSchema)
def get_payout(request, payout_id: str):
    """Получение заявки по ID"""
    return get_object_or_404(Payout, id=payout_id)


@router.post("/", response=PayoutResponseSchema)
def create_payout(request, payload: PayoutCreateSchema):
    """Создание заявки"""
    payout = Payout.objects.create(
        amount=payload.amount,
        currency=payload.currency,
        recipient_details=payload.recipient_details,
        description=payload.description,
        status='pending'
    )
    return payout


@router.patch("/{payout_id}/", response=PayoutResponseSchema)
def update_payout(request, payout_id: str, payload: PayoutUpdateSchema):
    """Обновление заявки"""
    payout = get_object_or_404(Payout, id=payout_id)

    for attr, value in payload.dict(exclude_unset=True).items():
        if hasattr(payout, attr):
            setattr(payout, attr, value)

    payout.save()
    return payout


@router.delete("/{payout_id}/")
def delete_payout(request, payout_id: str):
    """Удаление заявки"""
    payout = get_object_or_404(Payout, id=payout_id)
    payout.delete()
    return {"success": True}
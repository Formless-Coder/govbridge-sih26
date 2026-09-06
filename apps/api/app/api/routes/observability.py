from __future__ import annotations

from fastapi import APIRouter

from app.core.observability import get_observability_summary

router = APIRouter(tags=['observability'])


@router.get('/observability')
def get_observability():
    return get_observability_summary()

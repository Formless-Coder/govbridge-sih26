from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.entity_resolution import resolve_entities

router = APIRouter(tags=['entities'])


@router.post('/entities/resolve')
def resolve_entity_records(body: dict[str, Any]):
    records = body.get('records', [])
    if not isinstance(records, list):
        raise HTTPException(status_code=400, detail='records must be a list')
    return resolve_entities(records)

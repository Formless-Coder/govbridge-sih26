from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.connector import list_connectors

router = APIRouter(tags=['connectors'])


@router.get('/connectors')
def list_connector_registry(protocol: str | None = Query(default=None, description='Filter connectors by protocol')):
    return {'connectors': list_connectors(protocol=protocol)}

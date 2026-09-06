from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.workflow import create_workflow, get_workflow, list_workflows, update_stage

router = APIRouter(tags=['workflows'])


@router.post('/workflows', status_code=status.HTTP_201_CREATED)
def create_workflow_route(body: dict[str, Any]):
    case_id = body.get('case_id')
    service_id = body.get('service_id')
    sla_hours = int(body.get('sla_hours', 48))
    if not case_id or not service_id:
        raise HTTPException(status_code=400, detail='case_id and service_id are required')
    return create_workflow(case_id=case_id, service_id=service_id, sla_hours=sla_hours)


@router.get('/workflows')
def list_workflow_routes():
    return {'workflows': list_workflows()}


@router.get('/workflows/{case_id}')
def get_workflow_route(case_id: str):
    workflow = get_workflow(case_id)
    if not workflow:
        raise HTTPException(status_code=404, detail='Workflow not found')
    return workflow


@router.post('/workflows/{case_id}/stages')
def update_workflow_stage(case_id: str, body: dict[str, Any]):
    stage = body.get('stage')
    status_value = body.get('status', 'in_progress')
    if not stage:
        raise HTTPException(status_code=400, detail='stage is required')
    try:
        workflow = update_stage(case_id, stage=stage, status=status_value)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return workflow

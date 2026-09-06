from app.api.routes.cases import CASE_STORE, AUDIT_LOGS
from app.api.routes.services import list_services
from fastapi import APIRouter

router = APIRouter(tags=['citizen'])


@router.get('/citizen/dashboard')
def citizen_dashboard():
    services = list_services()
    cases = [
        {
            'case_id': case.get('case_id'),
            'status': case.get('status', 'DRAFT'),
            'service_id': case.get('service_id', 'scholarship'),
            'applicant_name': case.get('applicant_name', 'Citizen'),
            'decision': case.get('decision', {}),
        }
        for case in CASE_STORE.values()
    ]
    notifications = []
    for case in CASE_STORE.values():
        for event in case.get('timeline', []):
            notifications.append({
                'case_id': case.get('case_id'),
                'event': event.get('event', 'UPDATE'),
                'message': f"Case status updated to {case.get('status', 'DRAFT')} via {event.get('event', 'UPDATE')}",
                'status': case.get('status', 'DRAFT'),
            })

    active_cases = sum(1 for case in CASE_STORE.values() if case.get('status') not in {'COMPLETED', 'completed'})
    completed_cases = sum(1 for case in CASE_STORE.values() if case.get('status') in {'COMPLETED', 'completed'})

    return {
        'services': services,
        'cases': cases,
        'notifications': notifications,
        'stats': {
            'active_cases': active_cases,
            'completed_cases': completed_cases,
            'total_services': len(services),
        },
        'audit_count': len(AUDIT_LOGS),
    }

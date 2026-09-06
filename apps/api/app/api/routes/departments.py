from fastapi import APIRouter

router = APIRouter(tags=['departments'])


@router.get('/departments')
def list_departments():
    return {
        'departments': [
            {
                'id': 'income',
                'name': 'Income Verification',
                'service_id': 'scholarship',
                'description': 'Employment and income validation for public benefit eligibility.',
                'status': 'active',
            },
            {
                'id': 'housing',
                'name': 'Housing Needs',
                'service_id': 'scholarship',
                'description': 'Housing status review to support program eligibility.',
                'status': 'active',
            },
        ]
    }

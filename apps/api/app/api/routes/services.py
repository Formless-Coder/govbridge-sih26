from fastapi import APIRouter

router = APIRouter(tags=['services'])


@router.get('/services')
def list_services():
    return [
        {
            'id': 'scholarship',
            'name': 'Scholarship Eligibility',
            'description': 'Income and enrollment verification for scholarship eligibility.',
            'purpose': 'scholarship_eligibility',
            'provider': 'INCOME',
            'attributes': ['income.status'],
            'expiry_days': 30,
        }
    ]


@router.get('/services/{service_id}')
def get_service(service_id: str):
    if service_id != 'scholarship':
        return {'detail': 'not found'}
    return {
        'id': 'scholarship',
        'name': 'Scholarship Eligibility',
        'description': 'Income and enrollment verification for scholarship eligibility.',
        'purpose': 'scholarship_eligibility',
        'provider': 'INCOME',
        'attributes': ['income.status'],
        'required_documents': [
            'Income certificate',
            'Student ID or enrollment proof',
            'Bank account details',
            'Caste or disability certificate (if applicable)',
        ],
        'eligibility_summary': 'Open to eligible students with verified household income and active enrollment status.',
        'estimated_time_days': 12,
        'fee': 'No application fee',
        'deadline': 'Applications open throughout the year',
    }

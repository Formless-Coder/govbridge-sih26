from fastapi import APIRouter

from app.core.database import is_database_ready

router = APIRouter(tags=['health'])


@router.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'govbridge-api'}


@router.get('/ready')
def readiness_check():
    dependencies = {
        'postgres': 'ready' if is_database_ready() else 'unavailable',
        'redis': 'unknown',
    }
    return {'status': 'ok', 'dependencies': dependencies}

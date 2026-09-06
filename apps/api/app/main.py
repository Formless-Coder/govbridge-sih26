from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.database import init_db
from app.core.middleware import correlation_id_middleware
from app.core.observability import record_request

init_db()

from app.api.routes import admin, cases, citizen, connectors, decisions, departments, entities, events, health, me, observability, review_queue, services, workflows

app = FastAPI(title='GovBridge API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.middleware('http')(correlation_id_middleware)


@app.middleware('http')
async def request_logging_middleware(request: Request, call_next):
    response = await call_next(request)
    record_request(method=request.method, path=request.url.path, status_code=response.status_code)
    return response


app.include_router(health.router, prefix='/api/v1')
app.include_router(me.router, prefix='/api/v1')
app.include_router(services.router, prefix='/api/v1')
app.include_router(cases.router, prefix='/api/v1')
app.include_router(citizen.router, prefix='/api/v1')
app.include_router(events.router, prefix='/api/v1')
app.include_router(connectors.router, prefix='/api/v1')
app.include_router(entities.router, prefix='/api/v1')
app.include_router(workflows.router, prefix='/api/v1')
app.include_router(observability.router, prefix='/api/v1')
app.include_router(departments.router, prefix='/api/v1')
app.include_router(decisions.router, prefix='/api/v1')
app.include_router(review_queue.router, prefix='/api/v1')
app.include_router(admin.router, prefix='/api/v1')


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            'error_code': 'INTERNAL_SERVER_ERROR',
            'message': 'An unexpected error occurred.',
            'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
            'details': {},
        },
    )

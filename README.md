# GovBridge

GovBridge is a federated interoperability and orchestration control plane for public service workflows.

## Current milestone

This repository is initialized to meet the M0 foundation milestone from the project roadmap:

- FastAPI API skeleton with health and readiness endpoints
- correlation ID middleware
- Next.js web skeleton with a health-focused landing page
- Docker Compose for API, web, Postgres, and Redis
- GitHub Actions lint/test stub
- Alembic scaffolding for migration support

## Local setup

### API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web

```bash
cd apps/web
npm install
npm run dev
```

### Docker

```bash
cd infrastructure/docker
docker compose up --build
```

## Notes

- This project intentionally uses synthetic-only data and is not a production system.
- Secrets must remain in environment variables and never be committed to git.

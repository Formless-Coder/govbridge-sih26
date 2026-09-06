# GovBridge

## Executive Summary

GovBridge is a citizen-first digital public service platform designed to simplify and modernize how citizens access government services, how departments process applications, and how administrators monitor service delivery. The platform combines a modern web portal, a resilient API backend, and operational workflows that mirror the real lifecycle of public service delivery: intake, verification, review, decision-making, notifications, and auditability.

At its core, GovBridge helps government departments handle citizen requests more consistently, reduce manual coordination overhead, and provide a transparent service experience for users. The system is built to support a broad range of public-service use cases such as education assistance, grievance intake, eligibility assessment, review workflows, and departmental coordination.

## What We Have Built

The current implementation is a working prototype of a citizen portal and service orchestration platform with the following capabilities:

### Citizen experience
- Modern, government-style landing page and dashboard
- Service catalog with application flows
- Case tracking dashboard for citizens
- Notifications and status updates
- Secure-like login experience with role-aware access patterns

### Case and workflow management
- Case creation and lifecycle handling
- Workflow status tracking and SLA monitoring
- Department checks and review routing
- Decision recording and reassignment support
- Case completion and audit trail generation

### Operational intelligence
- Administrative audit dashboard
- Configuration management for service settings and notifications
- Observability hooks for request telemetry and request tracing
- Event, retry, and dead-letter handling for service workflows
- Entity resolution and duplicate detection for citizen records

### Integration layer
- Connector registry for department and data sources
- Synthetic protocol connectors and orchestration patterns
- Service-level abstraction for public workflow integration

### Technical stack
- Backend: FastAPI, SQLAlchemy, JWT-based auth scaffolding, SQLite for local persistence
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Infrastructure: Docker Compose for local orchestration
- Quality: Regression tests covering key workflow and platform behavior

## Architecture Overview

GovBridge follows a modular architecture that separates the user experience, API layers, core domain logic, and infrastructure concerns:

- apps/web: citizen, review, admin, and decision screens
- apps/api/app/api/routes: API routes for services, cases, review, admin, notifications, and health
- apps/api/app/core: shared business logic for workflow, policy, authorization, connectors, observability, and persistence
- infrastructure: local runtime and platform configuration
- tests/unit: focused validation of platform behavior and milestones

## How to Run Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- Git

### 1. Start the backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- http://localhost:8000
- Health endpoint: http://localhost:8000/api/v1/health

### 2. Start the frontend

```bash
cd apps/web
npm install
npm run dev -- --hostname 0.0.0.0 --port 3001
```

The portal will be available at:
- http://localhost:3001

### 3. Optional: run with Docker

```bash
cd infrastructure/docker
docker compose up --build
```

This starts the core local services and exposes the app through the configured Docker network.

## Key Project Structure

```text
.
├── apps/
│   ├── api/
│   │   ├── app/
│   │   └── requirements.txt
│   └── web/
├── infrastructure/
├── tests/
├── README.md
├── .gitignore
├── .env.example
└── .github/
```

## Core Capabilities by Module

### API routes
- services: public service catalog and application details
- citizen: citizen dashboard and status overview
- cases: case intake, tracking, and updates
- decisions: decision submission and governance actions
- review_queue: officer review worklist
- admin: audit and configuration management
- observability: metrics and telemetry summaries
- events: event lifecycle and retry handling
- workflows: SLA and stage tracking
- connectors: integration registry and source adapters
- entities: duplicate and identity resolution

### Business logic
- Auth and RBAC gatekeeping for protected flows
- Workflow lifecycle management
- Policy logic for eligibility and decision outcomes
- Connector normalization for structured data exchange
- Dead-letter and retry processing for event failures

## Professional Notes

GovBridge is positioned as a practical prototype for a public-service digital transformation initiative. It demonstrates how a government workflow platform can centralize data, decisions, and service operations while keeping the citizen experience simple and transparent.

This repository is intended as a strong technical foundation for further expansion into:
- production-grade authentication and identity management
- real database and cloud deployment architecture
- document upload and verification pipelines
- external departmental system integrations
- analytics and policy reporting
- operational dashboards and incident monitoring

## Testing and Validation

The project includes unit tests covering service flows, workflow behavior, security, entity resolution, admin configuration, observability, and case lifecycle events. These tests provide a baseline for validating the core platform behavior as it evolves.

```bash
cd /Users/amangiri/govbridge
pytest -q
```

## Security and Good Practice Notes

- Keep sensitive values in environment variables, not in source control.
- Use strong identity and access controls before production deployment.
- Treat this as a working prototype foundation rather than a production-hardened government system.
- Validate all integration pathways and data handling before deployment in live environments.

## Summary

GovBridge brings together the essential ingredients of a modern digital governance platform: citizen service access, departmental workflow orchestration, administrative oversight, and traceable public service operations. It is structured as a practical, extensible foundation that can evolve from a working MVP into a full-scale public service platform.


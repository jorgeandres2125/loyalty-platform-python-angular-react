# Sales Agent Management Platform — Python · Angular · React

Full-stack web platform for onboarding and managing sales agents and advisors: registration wizard, document management, e-signature, executive assignments, reporting and back-office catalogs. The backend is a FastAPI service built on Hexagonal Architecture, consumed by two equivalent front-ends, one in Angular and one in React.

## Tech stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.12+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, SQL Server (aioodbc / pyodbc), APScheduler |
| Security | JWT, OAuth 2.0 / OIDC, OTP and out-of-band verification, RBAC, CSRF protection, rate limiting (SlowAPI), mTLS, field-level encryption, audit logging |
| Front-end (Angular) | Angular 20, TypeScript, TanStack Query, Bootstrap 5, SCSS, Jasmine / Karma |
| Front-end (React) | React 18, TypeScript, Vite, React Router, TanStack Query, Zustand, React Bootstrap, Vitest, Testing Library |
| Quality | pytest (unit, integration, e2e, load), pytest-cov, Ruff, mypy (strict), Vulture, ESLint |
| Deployment | Kubernetes manifests (Deployment, HPA, PDB, CronJob, migration Job), Bicep / Terraform |

## Architecture

```
backend-python/
└── src/
    ├── domain/          # Entities, value objects, domain services, ports (inbound/outbound)
    ├── application/     # Use cases, application services, DTOs
    ├── adapters/        # FastAPI routers, schemas and middleware (inbound adapters)
    └── infrastructure/  # SQLAlchemy repositories, config, security, logging, reporting
```

- **Hexagonal Architecture (Ports & Adapters):** the domain does not depend on FastAPI or the database; infrastructure implements the outbound ports.
- **Feature-based front-ends:** both apps share the same structure (`app`, `pages`, `widgets`, `features`, `entities`, `shared`) and cover the same features, so the two frameworks can be compared on the same use cases.
- **Security middleware chain:** authentication, CSRF, security headers, HTTP method allow-listing, duplicate-parameter checks and security auditing.

## Main features

- Authentication with JWT, OIDC and OTP; session and device management; account lockout and password policies (expiration, history, temporary passwords).
- Role-based access control (RBAC) with least-privilege permissions.
- Multi-step agent registration and document upload with e-signature.
- Back-office catalogs (cities, banks, professions, programs, and more) and executive assignments.
- Excel report generation and an audit trail.

## Getting started

### Backend

```bash
cd backend-python
uv sync --extra dev
# create a .env file with the database connection and secrets
uv run alembic upgrade head
uv run uvicorn src.adapters.api.main:app --reload --port 8000
```

Tests:

```bash
uv run pytest -m "not slow" --cov=src
```

### Angular front-end

```bash
cd frontend-angular
npm install
npm start                     # http://localhost:4200 — proxies /api to the backend
```

### React front-end

```bash
cd frontend-react
npm install
npm run dev                   # http://localhost:5173
npm test
```

## Author

**Jorge Andrés Torres Morales** — Senior Software Engineer (.NET, Python, Angular, React)
[LinkedIn](https://www.linkedin.com/in/jorge-torres-morales/)

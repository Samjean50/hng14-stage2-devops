# HNG Stage 2 — Containerised Job Processing System

A microservices job processing system containerised with Docker and deployed via a full CI/CD pipeline.

## Services

| Service  | Language       | Port |
|----------|----------------|------|
| Frontend | Node.js/Express | 3000 |
| API      | Python/FastAPI  | 8000 |
| Worker   | Python          | —    |
| Redis    | Redis 7         | 6379 (internal only) |

## Prerequisites

- Docker 24+
- Docker Compose v2+
- Git

## Run locally from scratch

```bash
git clone https://github.com/Samjean50/hng14-stage2-devops.git
cd hng14-stage2-devops
cp .env.example .env
docker compose up --build
```

Visit `http://localhost:3000` — click Submit New Job and watch status update.

## What healthy startup looks like
redis     | Ready to accept connections
api       | Uvicorn running on http://0.0.0.0:8000
worker    | Processing job ...
frontend  | Frontend running on port 3000

All four containers should show as healthy:
```bash
docker compose ps
```

## API Endpoints

| Endpoint          | Method | Description              |
|-------------------|--------|--------------------------|
| /health           | GET    | Health check             |
| /jobs             | POST   | Create a new job         |
| /jobs/{job_id}    | GET    | Get job status           |

## Frontend Endpoints

| Endpoint      | Method | Description         |
|---------------|--------|---------------------|
| /             | GET    | Dashboard UI        |
| /submit       | POST   | Submit a job        |
| /status/:id   | GET    | Poll job status     |
| /health       | GET    | Health check        |

## CI/CD Pipeline

Stages run in strict order — any failure blocks subsequent stages:

`lint → test → build → security scan → integration test → deploy`

- **Lint:** flake8 (Python), eslint (JavaScript), hadolint (Dockerfiles)
- **Test:** pytest with mocked Redis, coverage report uploaded as artifact
- **Build:** All three images built and pushed to local registry, tagged with git SHA and latest
- **Security:** Trivy scans all images, fails on CRITICAL severity findings
- **Integration:** Full stack brought up, job submitted and polled to completion
- **Deploy:** Rolling update — new container must pass health check before old one stops

## Environment Variables

See `.env.example` for all required variables.

## Live URL

https://samjean.mooo.com
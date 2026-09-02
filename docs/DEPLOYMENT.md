# CleftPath — Deployment & Infrastructure Architecture

> **Document Version:** 1.0.0  
> **Status:** Approved Baseline Architecture  
> **Container Engine:** Docker / OCI Containers  
> **Orchestration Options:** Docker Compose (Local/Staging) & Cloud Run / AWS ECS (Production)

---

## 1. Infrastructure Topology & Environment Strategy

CleftPath is architected for frictionless local development while supporting zero-downtime, HIPAA-ready cloud deployments.

```mermaid
flowchart LR
    subgraph EdgeLayer ["Edge & CDN Layer (Cloudflare)"]
        DNS["Cloudflare DNS & WAF\n(DDoS Protection, SSL Termination TLS 1.3)"]
    end

    subgraph ComputeLayer ["Containerized Compute Layer"]
        FrontendService["Frontend SPA (Nginx Alpine)\nVercel / Cloudflare Pages / Container"]
        BackendService["Backend FastAPI (Uvicorn Async)\nGoogle Cloud Run / AWS ECS / Render"]
    end

    subgraph DataPersistence ["Managed Data & Storage Tier"]
        DB[("PostgreSQL 16 + pgvector\n(Supabase / AWS RDS / Neon)")]
        RedisCache[("Redis 7 (Upstash / ElastiCache)\n(Rate Limiting & Session Cache)")]
        BlobStore[("S3-Compatible Object Store\n(Cloudflare R2 / AWS S3 / MinIO)")]
    end

    DNS --> FrontendService
    DNS --> BackendService
    BackendService --> DB
    BackendService --> RedisCache
    BackendService --> BlobStore
```

---

## 2. Local Multi-Container Development (`docker-compose.yml`)

The entire stack runs locally with a single command: `docker compose up --build`.

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: cleftpath_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: cleftpath_admin
      POSTGRES_PASSWORD: devpassword123
      POSTGRES_DB: cleftpath_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cleftpath_admin -d cleftpath_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: cleftpath_redis
    restart: unless-stopped
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    container_name: cleftpath_minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadminpassword
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - miniodata:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: cleftpath_backend
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://cleftpath_admin:devpassword123@postgres:5432/cleftpath_db
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT_URL: http://minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadminpassword
      S3_BUCKET_NAME: cleftpath-documents
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      JWT_SECRET: devjwtsecretkeyforlocaldevelopmentonly12345
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: cleftpath_frontend
    restart: unless-stopped
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api/v1
    depends_on:
      - backend

volumes:
  pgdata:
  miniodata:
```

---

## 3. Production Multi-Stage Dockerfiles

### 3.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
# Stage 1: Build & dependency resolution
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime image (Distroless / Non-Root)
FROM python:3.11-slim AS runner

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . /app

# Run as non-root user for security
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -s /bin/sh appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/healthz || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
```

### 3.2 Frontend Production Dockerfile (`frontend/Dockerfile`)
```dockerfile
# Stage 1: Build Vite React App
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:1.25-alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 4. Cloud Deployment Profiles

### 4.1 Student Portfolio / Cost-Optimized Profile (Free to < $10/mo)
* **Frontend:** Vercel or Cloudflare Pages (Free global edge hosting with instant Git pushes).
* **Backend:** Render or Railway (FastAPI container service with auto-scaling down on idle).
* **Database:** Supabase or Neon (Managed PostgreSQL with free `pgvector` extension support).
* **Object Storage:** Cloudflare R2 (10 GB free S3-compatible storage with zero egress fees).
* **AI:** Google AI Studio Gemini API tier.

### 4.2 Production Enterprise Profile (HIPAA-Ready Scaling)
* **Compute:** Google Cloud Run (Fully serverless container scaling) or AWS ECS Fargate.
* **Database:** AWS RDS PostgreSQL 16 (Multi-AZ with automated snapshots and `pgvector`).
* **Object Storage:** AWS S3 with KMS Customer Managed Keys (CMK) and bucket-level Object Lock.
* **Secrets:** AWS Secrets Manager or Doppler.

---

## 5. Environment Variables & Secret Configuration Matrix

| Variable Name | Description | Environment | Sensitive? |
| :--- | :--- | :--- | :---: |
| `DATABASE_URL` | Async PostgreSQL connection string | Dev / Staging / Prod | **YES** |
| `GEMINI_API_KEY` | Google Gemini API key for PathGuide & OCR | Dev / Staging / Prod | **YES** |
| `JWT_SECRET` | 256-bit secret key for signing auth tokens | Dev / Staging / Prod | **YES** |
| `S3_ENDPOINT_URL` | S3 or MinIO API endpoint | Dev / Staging / Prod | No |
| `S3_ACCESS_KEY` | Storage IAM access key | Dev / Staging / Prod | **YES** |
| `S3_SECRET_KEY` | Storage IAM secret key | Dev / Staging / Prod | **YES** |
| `S3_BUCKET_NAME` | Name of private storage bucket | Dev / Staging / Prod | No |
| `CORS_ORIGINS` | Comma-separated allowed frontend domains | Dev / Staging / Prod | No |
| `ENVIRONMENT` | `development`, `staging`, or `production` | Dev / Staging / Prod | No |

---

## 6. Zero-Downtime Database Migration Workflow

To prevent breaking changes during live schema updates:
1. **Expand Phase (Alembic):** Add new nullable columns or new tables (`alembic upgrade head`).
2. **Deploy Phase:** Deploy backend application code utilizing the new schema fields.
3. **Contract Phase:** In a subsequent migration release, drop obsolete columns and enforce non-null constraints.

---

## 7. Observability, Monitoring & Health Checks

### 7.1 Health Endpoints
* `GET /api/v1/healthz` — Basic liveness probe (checks if web worker is responding).
* `GET /api/v1/readyz` — Readiness probe (validates active DB connection and pgvector extension readiness).

### 7.2 Telemetry & Metrics
* **Error Tracking:** Sentry SDK initialized in FastAPI and React clients for real-time crash reporting (with automatic PHI scrubbing enabled).
* **Metrics:** Prometheus exporter (`/metrics`) tracking HTTP request durations, active SSE connections, and Gemini API token consumption.
* **Structured Logs:** Formatted as single-line JSON logs compatible with Datadog, Grafana Loki, and CloudWatch.

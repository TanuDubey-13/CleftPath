# CleftPath — Deployment & Infrastructure Architecture

> **Document Version:** 2.0.0  
> **Status:** Production-Ready Baseline Architecture  
> **Target Cloud:** Google Cloud Run / AWS ECS / Render (Backend) & Vercel / Cloudflare Pages (Frontend)  
> **Database:** PostgreSQL 16 with `pgvector` Extension  

---

## 1. Production Topology & Architecture

```mermaid
flowchart LR
    subgraph EdgeLayer ["Edge & CDN Tier (Cloudflare / CloudFront)"]
        Edge["Edge DNS & WAF\n(DDoS Protection, TLS 1.3 Termination)"]
    end

    subgraph ComputeLayer ["Containerized Application Tier"]
        FrontendSPA["Frontend React SPA (Nginx / Static Edge)\nVercel / Cloudflare Pages"]
        BackendAPI["Backend FastAPI (Async Python 3.11)\nGoogle Cloud Run / AWS ECS / Render"]
    end

    subgraph PersistenceLayer ["Persistent Data Tier"]
        PostgresDB[("PostgreSQL 16 + pgvector\n(AWS RDS / Supabase / Neon)")]
        RedisCache[("Redis 7 Cache / Rate Limiting\n(Upstash / ElastiCache)")]
        DocStore[("Private S3-Compatible Storage\n(AWS S3 / Cloudflare R2)")]
    end

    subgraph AIService ["AI & Embeddings Tier"]
        GeminiAPI["Google Gemini 1.5 Flash\n(Server-Side RAG Only)"]
    end

    Edge --> FrontendSPA
    Edge --> BackendAPI
    FrontendSPA -->|HTTPS REST API /api/v1/*| BackendAPI
    BackendAPI -->|Async SQLAlchemy / asyncpg| PostgresDB
    BackendAPI -->|Redis Protocol| RedisCache
    BackendAPI -->|Presigned Uploads / S3 SDK| DocStore
    BackendAPI -->|Server-Side API Key| GeminiAPI
```

---

## 2. Prerequisites

| Component | Required Version | Purpose |
| :--- | :--- | :--- |
| **PostgreSQL** | `16.x` | Primary relational store for user, patient, and clinical records |
| **pgvector** | `>= 0.5.0` | Vector similarity search for 768-dim educational knowledge retrieval |
| **Python** | `3.11.x` | Backend runtime with FastAPI and asyncpg |
| **Node.js** | `20.x LTS` | Frontend build runtime for React + Vite + TypeScript |
| **Docker** (Optional) | `>= 24.x` | Containerized build and deployment runtime |

---

## 3. Environment Variables & Secret Configuration

### 3.1 Server-Only Secrets (Backend Production)

> [!CAUTION]
> These variables contain sensitive credentials. Store them in a secure Secret Manager (e.g. AWS Secrets Manager, Google Secret Manager, Doppler). **NEVER expose these to client-side bundles or source control.**

| Variable | Description | Example / Format | Mandatory? |
| :--- | :--- | :--- | :---: |
| `DATABASE_URL` | Async PostgreSQL connection string with `asyncpg` | `postgresql+asyncpg://user:pass@db.host.com:5432/cleftpath` | **YES** |
| `JWT_SECRET` | 256-bit cryptographically random signing key | Generate with `openssl rand -hex 32` | **YES** |
| `GEMINI_API_KEY` | Google Gemini API key for server-side PathGuide & OCR | `AIzaSy...` (from Google AI Studio / GCP) | **YES** |
| `S3_ACCESS_KEY` | Storage IAM access key | `AKIA...` | Optional |
| `S3_SECRET_KEY` | Storage IAM secret key | `wJalrXUtnFEMI...` | Optional |
| `POSTGRES_PASSWORD` | PostgreSQL user password | Secure random string | **YES** |

### 3.2 Server Non-Secret Configuration (Backend Production)

| Variable | Description | Recommended Production Value |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Application environment identifier | `production` |
| `DEBUG` | Enable debug mode and query echoing | `false` |
| `PROJECT_NAME` | Platform branding name | `CleftPath` |
| `API_V1_STR` | API route prefix | `/api/v1` |
| `CORS_ORIGINS` | Permitted frontend origins (comma-separated or JSON) | `["https://app.cleftpath.org","https://cleftpath.org"]` |
| `COOKIE_SECURE` | Enforce HTTPS on authentication cookies | `true` |
| `COOKIE_SAMESITE` | Cookie SameSite policy | `lax` |
| `COOKIE_NAME` | Auth token cookie key name | `cleftpath_access_token` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `REDIS_URL` | Redis instance connection URI | `redis://default:pass@redis.host.com:6379/0` |

### 3.3 Safe Public Frontend Variables (Client Build Time)

> [!NOTE]
> Frontend variables starting with `VITE_` are compiled into static JavaScript bundles. They must contain **zero secrets**.

| Variable | Description | Recommended Production Value |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Base endpoint URL for backend API | `https://api.cleftpath.org/api/v1` |

---

## 4. Production Database Setup & Migration Procedure

### Step 1: Provision Managed PostgreSQL 16
Provision a managed PostgreSQL 16 database instance (e.g. AWS RDS, Supabase, Neon).

### Step 2: Enable `pgvector` Extension
Connect to the database as superuser/admin and execute:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 3: Run Alembic Database Migrations
Run Alembic migrations from the backend container/environment:
```bash
cd backend
alembic upgrade head
```

Verify that all tables (`users`, `patients`, `journey_stages`, `health_articles`, `appointments`, `feeding_logs`, `voice_sessions`, `pathguide_threads`, `village_posts`, etc.) and vector indices are created.

### Step 4: Seed Baseline Reference Stages & Educational Library (Optional)
To populate the standard ACPA 8 clinical care stages and verified educational health articles:
```bash
python -m app.db.seed
```

> [!WARNING]
> **Production Safety Notice:** Never seed synthetic or demo patient records into a live production patient database unless initializing a controlled demonstration staging environment.

---

## 5. Backend Production Deployment

### Option A: Google Cloud Run (Recommended Serverless)
1. Build and push container image:
   ```bash
   gcloud builds submit --tag gcr.io/$PROJECT_ID/cleftpath-backend ./backend
   ```
2. Deploy service:
   ```bash
   gcloud run deploy cleftpath-backend \
     --image gcr.io/$PROJECT_ID/cleftpath-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-secrets="DATABASE_URL=cleftpath-db-url:latest,JWT_SECRET=cleftpath-jwt-secret:latest,GEMINI_API_KEY=cleftpath-gemini-key:latest" \
     --set-env-vars="ENVIRONMENT=production,DEBUG=false,COOKIE_SECURE=true,CORS_ORIGINS=['https://app.cleftpath.org']"
   ```

### Option B: Docker Container on AWS ECS / Render
Build using the optimized production multi-stage Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
```

---

## 6. Frontend Production Deployment

### Option A: Vercel / Cloudflare Pages (Recommended Static Edge)
1. Set Root Directory to `frontend`.
2. Build command: `npm run build` (outputs to `dist/`).
3. Set environment variable: `VITE_API_BASE_URL=https://api.cleftpath.org/api/v1`.

### Option B: Docker + Nginx Container
Build using `frontend/Dockerfile`:
```bash
docker build -t cleftpath-frontend ./frontend
docker run -p 80:80 cleftpath-frontend
```

---

## 7. Security, CORS & HTTPS Hardening

1. **HTTPS Enforcement:** Production traffic must terminate with TLS 1.3. Backend must be behind a reverse proxy/load balancer forwarding `X-Forwarded-Proto: https`.
2. **CORS Isolation:** Set `CORS_ORIGINS` strictly to the production frontend domain (e.g. `https://app.cleftpath.org`). Do not use `*` or include `localhost` in production.
3. **Cookie Security:** Set `COOKIE_SECURE=true` and `COOKIE_SAMESITE=lax`.
4. **Debug Deactivation:** Ensure `DEBUG=false` in production to prevent stack trace leakage and SQLAlchemy query logging.

---

## 8. Production Security & Launch Checklist

- [ ] **HTTPS / TLS:** Valid SSL certificate installed; HTTP redirects to HTTPS.
- [ ] **Secure Cookies:** `COOKIE_SECURE=true` set in production backend.
- [ ] **Strong Secrets:** Cryptographically random 256-bit `JWT_SECRET` configured in Secret Manager.
- [ ] **Database Credentials:** `DATABASE_URL` stored server-side only; direct frontend DB access prohibited.
- [ ] **Gemini API Key:** `GEMINI_API_KEY` stored server-side only; zero client bundle leakage.
- [ ] **pgvector Extension:** Verified `vector` extension enabled on PostgreSQL 16.
- [ ] **Database Migrations:** `alembic upgrade head` executed successfully against target database.
- [ ] **CORS Origins:** Restricted strictly to production frontend URL.
- [ ] **Debug Disabled:** `DEBUG=false` set in production environment.
- [ ] **Zero Real Patient Data:** Test fixtures and staging environments contain zero actual PHI.
- [ ] **Local Voice Privacy:** Voice Journey audio verified to process exclusively in-browser.
- [ ] **Village Moderation:** Admin and Clinician moderation endpoints verified to reject standard caregivers (403).
- [ ] **Automated Tests:** 100% test pass rate on backend (`pytest`) and frontend (`vitest`, `tsc`).

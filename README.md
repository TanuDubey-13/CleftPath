# CleftPath

> *“Every journey deserves a path forward.”*

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL 16 + pgvector](https://img.shields.io/badge/Database-PostgreSQL_16_+_pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![Tailwind CSS](https://img.shields.io/badge/Design_System-Tailwind_CSS-38B2AC.svg)](https://tailwindcss.com/)

---

## 1. Project Overview

**CleftPath** is an enterprise-grade, privacy-first, full-stack healthcare technology platform designed to help individuals and families navigate the long-term cleft lip and palate journey from prenatal diagnosis through adulthood.

The cleft care pathway typically spans 18–21+ years, requiring coordination across 10+ medical and surgical specialties (Plastic Surgery, ENT, SLP, Orthodontics, Pediatric Dentistry, Audiology, Genetics, Pediatrics). CleftPath organizes clinical milestones, specialized feeding logs, medical documents, speech progress, and peer support within an empathetic, trauma-informed digital sanctuary.

### 1.1 Non-Diagnostic Medical Boundary
CleftPath is **strictly supportive and educational**. It does **NOT** diagnose medical conditions (e.g. *velopharyngeal insufficiency*, *fistula*) or prescribe medications. It reinforces and clarifies guidance from accredited multidisciplinary cleft teams (e.g. ACPA teams).

---

## 2. Technology Stack

### Frontend (Cursor Engineering Environment)
* **Framework:** React 18 with TypeScript 5
* **Build Tool:** Vite
* **Styling & Design Tokens:** Tailwind CSS (Warm Ivory `#FAF7F2`, Deep Teal `#0F4C5C`, Soft Sage `#81B29A`, Warm Coral `#E07A5F`)
* **Routing:** React Router v6
* **Server State & Caching:** TanStack Query v5
* **Data Visualization:** Recharts
* **Icons:** Lucide React

### Backend (Antigravity Engineering Environment)
* **Framework:** Python 3.11+ / FastAPI
* **ORM & Database:** SQLAlchemy 2.0 (Async) + PostgreSQL 16 + `pgvector`
* **Schema Evolution:** Alembic migrations
* **Data Validation:** Pydantic v2
* **Structured Logging:** Loguru with automated PHI/PII redaction interceptors
* **AI Orchestration:** Google Gemini 1.5/2.0 API + RAG hybrid vector retrieval

---

## 3. Repository Structure

```text
CleftPath/
├── frontend/             # React 18 + TypeScript + Vite + Tailwind SPA
│   ├── src/
│   │   ├── api/          # API endpoint client functions
│   │   ├── components/   # UI primitives (Button, Card, Badge, Alert) & AppShell
│   │   ├── hooks/        # Custom React hooks (useHealth, etc.)
│   │   ├── lib/          # Axios client & TanStack QueryClient
│   │   ├── pages/        # Route pages (Dashboard, Journey, Library, Care, etc.)
│   │   ├── routes/       # React Router hierarchy
│   │   └── types/        # TypeScript DTO schemas
│   ├── package.json
│   ├── tailwind.config.ts
│   └── vite.config.ts
│
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/       # REST API endpoints & routers
│   │   ├── core/         # Config, logging, and error handlers
│   │   ├── db/           # Async database engine & sessionmaker
│   │   ├── middleware/   # CORS & request timing middlewares
│   │   ├── models/       # SQLAlchemy 2.0 declarative models
│   │   ├── schemas/      # Pydantic v2 request/response schemas
│   │   ├── services/     # Domain business logic & health checks
│   │   └── main.py       # FastAPI application factory
│   ├── alembic/          # Database migrations & pgvector setup
│   ├── tests/            # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── ai-service/           # PathGuide RAG & AI evaluation harness
├── knowledge-base/       # Medically verified ACPA clinical guides
├── docs/                 # Architectural specifications & design system
├── tests/                # System-wide E2E tests (Playwright)
├── .env.example          # Environment variables template
├── docker-compose.yml    # Full-stack local multi-container development
├── AGENTS.md             # AI agent and developer operating protocol
└── README.md
```

---

## 4. Local Development Setup

### Prerequisites
* **Node.js:** v20+ (`npm` v10+)
* **Python:** 3.11+
* **Docker & Docker Compose:** Installed and running

### Quick Start with Docker Compose
To spin up the entire full-stack environment with PostgreSQL (pgvector), Redis, FastAPI backend, and React frontend:

```bash
# 1. Clone the repository
git clone https://github.com/TanuDubey-13/CleftPath.git
cd CleftPath

# 2. Configure environment
cp .env.example .env

# 3. Start containers
docker compose up --build
```
* **Frontend:** [http://localhost:5173](http://localhost:5173)
* **Backend API:** [http://localhost:8000](http://localhost:8000)
* **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Manual Setup (Running Services Independently)

#### 1. Backend Setup
```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run migrations (ensure local Postgres is running)
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 5. Testing Strategy

### Running Backend Tests
```bash
cd backend
pytest -v --cov=app
```

### Running Frontend Tests & Type Checking
```bash
cd frontend
npm run typecheck
npm run test
```

---

## 6. Core Engineering & Safety Rules

As defined in [`AGENTS.md`](AGENTS.md):
1. **Never Diagnose or Prescribe:** PathGuide reinforces the role of the patient's accredited cleft team.
2. **Emergency Escalation:** Acute symptoms immediately trigger emergency hotline banners.
3. **Zero Real Patient Data:** Only synthetic test fixtures are permitted during development and testing.
4. **No Direct DB Access from Frontend:** All frontend state transitions must route through authenticated FastAPI endpoints.

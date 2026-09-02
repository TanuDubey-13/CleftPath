# CleftPath — REST API Specification

> **API Version:** v1 (`/api/v1`)  
> **Protocol:** HTTPS (TLS 1.3) / Server-Sent Events (SSE)  
> **Format:** JSON (`application/json`) / Event Stream (`text/event-stream`)  
> **Documentation Engine:** OpenAPI 3.1 (FastAPI Swagger UI at `/docs` & ReDoc at `/redoc`)

---

## 1. Global Standards & Envelope Formats

### 1.1 Base URL & Versioning
* Local Development: `http://localhost:8000/api/v1`
* Production: `https://api.cleftpath.org/api/v1`

### 1.2 Authentication Header
Requests to protected endpoints must supply a valid JWT access token:
```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
```
Alternatively, browser clients authenticate via an `HttpOnly`, `SameSite=Strict`, `Secure` cookie named `cleftpath_access_token`.

### 1.3 Standard Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 142
  }
}
```

### 1.4 Standard Error Response Envelope
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Patient with ID 'pt_9872' does not exist or access is forbidden.",
    "details": [
      {
        "field": "patient_id",
        "issue": "Invalid UUID format"
      }
    ]
  },
  "timestamp": "2026-09-02T12:00:00Z",
  "request_id": "req_84a9e10f"
}
```

### 1.5 HTTP Status Codes
* `200 OK` — Standard successful GET/PUT/PATCH response.
* `201 Created` — Resource successfully created.
* `204 No Content` — Successful deletion.
* `400 Bad Request` — Schema validation failure or malformed payload.
* `401 Unauthorized` — Missing, invalid, or expired JWT token.
* `403 Forbidden` — Authenticated user lacks permission to the resource.
* `404 Not Found` — Resource does not exist.
* `422 Unprocessable Entity` — Pydantic validation error on request body.
* `429 Too Many Requests` — Rate limit exceeded (Rate limit headers supplied).
* `500 Internal Server Error` — Unhandled server exception (logged with trace ID).

---

## 2. API Endpoint Matrix by Product Module

### 2.1 Authentication & Consent (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Create a new user account with role selection | No |
| `POST` | `/auth/login` | Authenticate with email/password; returns JWT + set cookie | No |
| `POST` | `/auth/refresh` | Exchange refresh token for fresh access token | Yes (Refresh Token) |
| `POST` | `/auth/logout` | Invalidate active refresh token and clear cookies | Yes |
| `GET` | `/auth/me` | Fetch authenticated user profile and active permissions | Yes |
| `POST` | `/auth/consent` | Record user agreement to Terms, Privacy & AI Disclaimer | Yes |
| `POST` | `/auth/forgot-password` | Request password reset email | No |
| `POST` | `/auth/reset-password` | Execute password reset via one-time secure token | No |

#### `POST /auth/register`
**Request Body:**
```json
{
  "email": "sarah.parent@example.com",
  "password": "SecurePassword123!",
  "first_name": "Sarah",
  "last_name": "Jenkins",
  "role": "caregiver",
  "consents": {
    "terms_accepted": true,
    "privacy_policy_accepted": true,
    "ai_safety_disclaimer_accepted": true
  }
}
```
**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "usr_c83f91ae-b293",
    "email": "sarah.parent@example.com",
    "role": "caregiver",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

---

### 2.2 Patient Management (`/api/v1/patients`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/patients` | List all patient/child profiles linked to user | Yes |
| `POST` | `/patients` | Register a new patient/child profile | Yes |
| `GET` | `/patients/{patient_id}` | Get patient medical baseline and cleft classification | Yes |
| `PUT` | `/patients/{patient_id}` | Update patient profile details | Yes |
| `DELETE`| `/patients/{patient_id}` | Soft delete/archive patient profile | Yes |

#### `POST /patients`
**Request Body:**
```json
{
  "display_name": "Leo",
  "date_of_birth": "2026-03-15",
  "gender": "male",
  "cleft_classification": {
    "lip": "unilateral_left_complete",
    "palate": "hard_and_soft_complete",
    "alveolus": "involved"
  },
  "primary_cleft_team_center": "Children's Craniofacial Center"
}
```

---

### 2.3 My Journey (`/api/v1/patients/{patient_id}/journey`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/{patient_id}/journey/stages` | Get all clinical stages and completion percentages | Yes |
| `GET` | `/{patient_id}/journey/milestones` | List all timeline milestones with filter options | Yes |
| `POST` | `/{patient_id}/journey/milestones` | Create a custom family milestone or reminder | Yes |
| `PATCH`| `/journey/milestones/{milestone_id}`| Update milestone status (`UPCOMING`, `IN_PROGRESS`, `COMPLETED`)| Yes |
| `POST` | `/journey/milestones/{milestone_id}/notes` | Attach a personal family memory/note/photo to milestone | Yes |

---

### 2.4 Health Library (`/api/v1/health-library` and `/api/v1/library`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health-library/articles` | List articles with pagination, category, stage, and search keyword filters | Yes |
| `GET` | `/health-library/articles/{article_id}` | Get full article markdown content, reading time, citations, and clinical verification | Yes |
| `GET` | `/health-library/categories` | List all library categories with published article counts | Yes |

---

### 2.5 Appointments & Care Team (`/api/v1/appointments`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/appointments` | List appointments with timeframe (upcoming/past/all), status, and pagination | Yes |
| `GET` | `/appointments/care-team` | List multidisciplinary specialists linked to patient | Yes |
| `GET` | `/appointments/{id}` | Get appointment details with prep questions and care team info | Yes |
| `POST` | `/appointments` | Schedule a new appointment with date, duration, and prep questions | Yes |
| `PATCH`| `/appointments/{id}` | Update appointment fields or transition status | Yes |
| `POST` | `/appointments/{id}/cancel` | Cancel a scheduled appointment with audit logging | Yes |

---

### 2.6 Baby & Parent Care (`/api/v1/care` and `/api/v1/baby-care`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/care/overview` | Aggregated metrics (today's volume, latest weight, NAM hours, guidance) | Yes |
| `GET` | `/care/feeding` | List feeding logs with date range and pagination | Yes |
| `GET` | `/care/feeding/{log_id}` | Get single feeding log detail | Yes |
| `POST` | `/care/feeding` | Log a specialty feeding session (volume, bottle type, duration, burps) | Yes |
| `PATCH`| `/care/feeding/{log_id}` | Update feeding log fields | Yes |
| `DELETE`| `/care/feeding/{log_id}` | Delete feeding log record | Yes |
| `GET` | `/care/growth` | List growth and physical measurement records | Yes |
| `GET` | `/care/growth/{record_id}` | Get single growth measurement detail | Yes |
| `POST` | `/care/growth` | Record weight, length/height, or head circumference | Yes |
| `PATCH`| `/care/growth/{record_id}` | Update growth measurement fields | Yes |
| `DELETE`| `/care/growth/{record_id}` | Delete growth measurement record | Yes |
| `GET` | `/care/nam` | List NAM (Nasoalveolar Molding) wear logs | Yes |
| `GET` | `/care/nam/{log_id}` | Get single NAM wear log detail | Yes |
| `POST` | `/care/nam` | Log daily NAM wear hours, tape change, and skin condition | Yes |
| `PATCH`| `/care/nam/{log_id}` | Update NAM wear log | Yes |
| `DELETE`| `/care/nam/{log_id}` | Delete NAM wear log record | Yes |

#### `POST /api/v1/care/feeding`
**Request Body:**
```json
{
  "logged_at": "2026-09-02T08:30:00Z",
  "bottle_type": "dr_browns_specialty",
  "volume_ml": 110,
  "duration_minutes": 25,
  "burping_breaks": 3,
  "reflux_severity": "mild",
  "notes": "Fed in upright 60-degree angle, latched to blue valve smoothly."
}
```

---

### 2.7 Voice Journey (`/api/v1/voice`)

> **Non-Diagnostic Notice:** Voice Journey endpoints provide educational practice prompts and session tracking only. No speech diagnosis, clinical acoustic scoring, or automated treatment recommendations are performed. Audio recordings are previewed locally via browser Web MediaRecorder and are never sent to external AI/Gemini or public endpoints.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/voice/overview` | Practice metrics, total minutes, and educational guidance | Yes |
| `GET` | `/voice/exercises` | List speech practice exercises with stage/difficulty filters | Yes |
| `GET` | `/voice/exercises/{exercise_id}` | Get exercise details, phonemes, and caregiver instructions | Yes |
| `GET` | `/voice/sessions` | List user's practice sessions with pagination and date filter | Yes |
| `GET` | `/voice/sessions/{session_id}` | Get single session detail with IDOR verification | Yes |
| `POST` | `/voice/sessions` | Log a voice practice session | Yes |
| `PATCH` | `/voice/sessions/{session_id}` | Update session duration, repetition count, or notes | Yes |
| `DELETE` | `/voice/sessions/{session_id}` | Delete a practice session record | Yes |

#### `POST /api/v1/voice/sessions`
**Request Body:**
```json
{
  "exercise_id": "8a32d184-7e9c-4b53-a5a4-969c3a30f301",
  "duration_seconds": 45,
  "repetition_count": 3,
  "parent_notes": "Child laughed and practiced repetitive /pa/ and /ba/ sounds.",
  "audio_s3_key": "local_session/1725280000"
}
```

---

### 2.8 PathGuide AI Chat (`/api/v1/pathguide`)

> **Non-Diagnostic Notice:** PathGuide is an educational navigation companion. It never diagnoses medical conditions, speech disorders, or surgical complications, and never prescribes medications or treatments. Acute symptom triggers act as conservative safety routing to urgent medical care. Retrieval is strictly bounded to published Health Library articles (`health_articles.is_published == True`).

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/pathguide/suggested-prompts` | Get educational starter prompts | Yes |
| `GET` | `/pathguide/threads` | List active user's conversation threads | Yes |
| `POST` | `/pathguide/threads` | Create a new conversation thread | Yes |
| `GET` | `/pathguide/threads/{thread_id}` | Get thread details and message count | Yes |
| `PATCH` | `/pathguide/threads/{thread_id}` | Rename conversation thread title | Yes |
| `DELETE` | `/pathguide/threads/{thread_id}` | Delete conversation thread | Yes |
| `GET` | `/pathguide/threads/{thread_id}/messages` | List messages in thread with citations | Yes |
| `POST` | `/pathguide/threads/{thread_id}/messages` | Send message and receive RAG-grounded response | Yes |

#### `POST /api/v1/pathguide/threads/{thread_id}/messages`
**Request Body:**
```json
{
  "content": "How do specialized cleft feeders like Dr. Brown's or Haberman work?"
}
```

**Response Body:**
```json
{
  "success": true,
  "data": {
    "id": "e67d2b45-12fa-48b2-8fa0-90c1284d7801",
    "thread_id": "8a32d184-7e9c-4b53-a5a4-969c3a30f301",
    "role": "assistant",
    "content": "Based on CleftPath educational resources (Understanding Specialized Cleft Feeders), specialized feeding systems utilize unidirectional valves and positive pressure assists...\n\nPlease discuss your child's specific feeding routine with your pediatric cleft care team.",
    "citations": [
      {
        "article_id": "4b53d184-7e9c-4b53-a5a4-969c3a30f302",
        "title": "Understanding Specialized Cleft Feeders",
        "category": "Feeding & Nutrition",
        "slug": "understanding-specialized-cleft-feeders",
        "summary": "A comprehensive clinical comparison of unidirectional valves and assisted squeezing techniques."
      }
    ],
    "safety_flags": {
      "emergency_trigger_detected": false,
      "grounded_sources_count": 1,
      "model": "gemini-1.5-flash"
    },
    "tokens_used": 145,
    "created_at": "2026-09-02T10:00:00Z"
  }
}
```

---

### 2.9 Document Vault & OCR Pipeline (`/api/v1/documents`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/{patient_id}/documents` | List stored clinical documents with OCR processing status | Yes |
| `POST` | `/{patient_id}/documents/upload-intent` | Get encrypted presigned S3 upload URL | Yes |
| `POST` | `/documents/{id}/process-ocr` | Trigger Gemini multimodal OCR & structured extraction | Yes |
| `GET` | `/documents/{id}/preview-url` | Get temporary presigned download/view URL (15m expiry) | Yes |
| `POST` | `/documents/{id}/commit-to-journey` | Accept extracted milestone items into My Journey roadmap | Yes |
| `DELETE`| `/documents/{id}` | Permanently delete document file and vector chunks | Yes |

---

### 2.10 The Village (`/api/v1/village`)

> **Community Peer Support Notice:** The Village is an educational and peer-support environment. Community posts and comments reflect lived personal experiences and are never a substitute for clinical advice. All mutations enforce strict IDOR server-side ownership. Moderation endpoints are restricted to `ADMIN` and `CLINICIAN` roles. Zero AI diagnosis or RAG functionality is attached.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/village/channels` | List community channels with post counts | Yes |
| `GET` | `/village/channels/{channel_id}` | Get single channel details | Yes |
| `GET` | `/village/channels/{channel_id}/posts` | List posts within a specific channel | Yes |
| `GET` | `/village/posts` | List community posts across channels with search filter | Yes |
| `GET` | `/village/posts/{post_id}` | Get post details and user reaction state | Yes |
| `POST` | `/village/posts` | Create a new community post | Yes |
| `PATCH` | `/village/posts/{post_id}` | Edit own community post | Yes |
| `DELETE` | `/village/posts/{post_id}` | Delete own community post | Yes |
| `GET` | `/village/posts/{post_id}/comments` | List comments for a post | Yes |
| `POST` | `/village/posts/{post_id}/comments` | Add a comment to a post | Yes |
| `PATCH` | `/village/comments/{comment_id}` | Edit own comment | Yes |
| `DELETE` | `/village/comments/{comment_id}` | Delete own comment | Yes |
| `POST` | `/village/posts/{post_id}/reactions` | Toggle supportive reaction (`heart`, `hug`, `celebrate`, `strength`, `helpful`) | Yes |
| `POST` | `/village/posts/{post_id}/report` | Report inappropriate post content | Yes |
| `POST` | `/village/comments/{comment_id}/report` | Report inappropriate comment content | Yes |
| `GET` | `/village/moderation/reports` | Moderation queue: list reports (Admin/Clinician) | Yes (Admin/Clinician) |
| `POST` | `/village/moderation/reports/{report_id}/resolve` | Resolve moderation report / hide content (Admin/Clinician) | Yes (Admin/Clinician) |

#### `POST /api/v1/village/posts`
**Request Body:**
```json
{
  "channel_id": "8a32d184-7e9c-4b53-a5a4-969c3a30f301",
  "title": "Tips for keeping soft arm restraints comfortable during sleep?",
  "content": "We are getting ready for Leo's lip repair in 4 weeks. Any advice from parents who have gone through this on making sleep more comfortable?",
  "author_alias": "Parent Sarah"
}
```

**Response Body:**
```json
{
  "success": true,
  "data": {
    "id": "e67d2b45-12fa-48b2-8fa0-90c1284d7801",
    "channel_id": "8a32d184-7e9c-4b53-a5a4-969c3a30f301",
    "channel_name": "Surgery Prep & Recovery",
    "channel_slug": "surgery-prep",
    "user_id": "3c84f67e-12fa-48b2-8fa0-90c1284d7800",
    "author_alias": "Parent Sarah",
    "author_avatar_seed": "avatar1",
    "title": "Tips for keeping soft arm restraints comfortable during sleep?",
    "content": "We are getting ready for Leo's lip repair in 4 weeks. Any advice from parents who have gone through this on making sleep more comfortable?",
    "status": "published",
    "is_flagged": false,
    "upvotes_count": 0,
    "comments_count": 0,
    "has_reacted": false,
    "created_at": "2026-09-02T10:00:00Z",
    "updated_at": "2026-09-02T10:00:00Z"
  }
}
```

---

### 2.11 User Profile, Data Export & Privacy (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/users/profile` | Get account settings and linked notification preferences | Yes |
| `PUT` | `/users/profile` | Update account preferences | Yes |
| `POST` | `/users/export-data` | Request complete HIPAA/GDPR data export ZIP | Yes |
| `DELETE`| `/users/account` | Request irreversible account deletion (Right to Erasure) | Yes |

---

### 2.12 Admin & Moderation (`/api/v1/admin`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/admin/moderation/queue` | List posts flagged by AI safety filter or user reports | Admin / Mod |
| `POST` | `/admin/moderation/action` | Approve, quarantine, or delete flagged post | Admin / Mod |
| `GET` | `/admin/audit-logs` | Query immutable PHI access and security audit events | Admin |
| `GET` | `/admin/metrics` | System health, RAG latency, and user activity counts | Admin |

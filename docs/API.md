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

### 2.4 Health Library (`/api/v1/library`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/library/articles` | List articles with stage, category, and keyword filters | No (Public) |
| `GET` | `/library/articles/{slug}` | Get full article content, citations, and related resources | No (Public) |
| `GET` | `/library/categories` | List all library categories and stage tags | No (Public) |
| `POST` | `/library/search` | Semantic hybrid search across verified clinical library | No (Public) |
| `POST` | `/library/bookmarks/{article_id}` | Save article to user bookmarks | Yes |

---

### 2.5 Appointments & Care Team (`/api/v1/patients/{patient_id}/appointments`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/{patient_id}/appointments` | List past and upcoming clinical visits | Yes |
| `POST` | `/{patient_id}/appointments` | Schedule a new specialist appointment | Yes |
| `GET` | `/appointments/{id}` | Get appointment details and generated prep sheet | Yes |
| `POST` | `/appointments/{id}/generate-prep-sheet` | Trigger AI generation of 5 tailored specialist questions | Yes |
| `POST` | `/appointments/{id}/visit-summary` | Save doctor summary notes or transcribed voice memo | Yes |
| `GET` | `/{patient_id}/care-team` | List all linked multidisciplinary specialists | Yes |
| `POST` | `/{patient_id}/care-team` | Add specialist contact (Surgeon, SLP, ENT, Orthodontist) | Yes |

---

### 2.6 Baby & Parent Care (`/api/v1/patients/{patient_id}/baby-care`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/{patient_id}/baby-care/feeding` | Get feeding logs with aggregate daily volume metrics | Yes |
| `POST` | `/{patient_id}/baby-care/feeding` | Log a feeding session (volume, bottle type, duration) | Yes |
| `GET` | `/{patient_id}/baby-care/growth` | Get weight/height logs plotted against WHO percentiles | Yes |
| `POST` | `/{patient_id}/baby-care/growth` | Record a new weight or length measurement | Yes |
| `GET` | `/{patient_id}/baby-care/nam` | Get NAM (Nasoalveolar Molding) wear logs | Yes |
| `POST` | `/{patient_id}/baby-care/nam` | Log NAM appliance tape change, skin check, and hours | Yes |

#### `POST /{patient_id}/baby-care/feeding`
**Request Body:**
```json
{
  "logged_at": "2026-09-02T08:30:00Z",
  "feeding_method": "dr_browns_specialty_feeder",
  "volume_ml": 110,
  "duration_minutes": 25,
  "burping_breaks": 3,
  "reflux_level": "mild",
  "notes": "Fed in upright 60-degree angle, transitioned to blue valve smoothly."
}
```

---

### 2.7 Voice Journey (`/api/v1/voice`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/voice/exercises` | List SLP-recommended speech practice prompts | Yes |
| `GET` | `/voice/exercises/{id}` | Get audio sample, phoneme targets, and visual game assets | Yes |
| `POST` | `/{patient_id}/voice/sessions` | Upload recorded practice session audio for feature analysis | Yes |
| `GET` | `/{patient_id}/voice/progress` | Get longitudinal articulation consistency & volume stats | Yes |

---

### 2.8 PathGuide AI Chat (`/api/v1/pathguide`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/pathguide/threads` | List active chat threads for current user/patient | Yes |
| `POST` | `/pathguide/threads` | Create a new conversational thread with patient context | Yes |
| `GET` | `/pathguide/threads/{thread_id}/messages` | Get message history with citations | Yes |
| `POST` | `/pathguide/threads/{thread_id}/stream` | **SSE Stream:** Send message and stream grounded response | Yes |
| `GET` | `/pathguide/suggested-prompts` | Get contextual suggested questions based on child's stage | Yes |

#### `POST /pathguide/threads/{thread_id}/stream`
**SSE Streaming Response Format:**
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: metadata
data: {"citations": [{"source_title": "ACPA Feeding Guidelines", "url": "/library/feeding-infants-cleft", "page": 4}]}

event: token
data: {"text": "When "}

event: token
data: {"text": "feeding with a "}

event: token
data: {"text": "SpecialNeeds feeder, keep your baby at a 45-to-60 degree upright angle..."}

event: done
data: {"message_id": "msg_90a1b2", "safety_status": "grounded_safe"}
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

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/village/channels` | List stage-based community channels | Yes |
| `GET` | `/village/posts` | Paginated feed of posts filtered by channel/tag | Yes |
| `POST` | `/village/posts` | Create new post (subject to automated PII & safety scan) | Yes |
| `GET` | `/village/posts/{id}` | Get post details and threaded comments | Yes |
| `POST` | `/village/posts/{id}/comments` | Add comment to a community post | Yes |
| `POST` | `/village/posts/{id}/react` | Toggle supportive reaction (Heart, Hug, Fist Bump) | Yes |
| `POST` | `/village/reports` | Flag a post or comment for moderator review | Yes |

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

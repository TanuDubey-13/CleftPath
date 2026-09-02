# CleftPath — Security, Privacy & Compliance Architecture

> **Document Version:** 1.0.0  
> **Status:** Approved Baseline Architecture  
> **Compliance Target:** HIPAA Security & Privacy Rule, GDPR, CCPA, OWASP Top 10 (2025/2026)  
> **Classification:** Confidential / Healthcare Engineering Standard

---

## 1. Security Philosophy & Privacy-by-Design

CleftPath handles sensitive pediatric, surgical, and familial health data. Protecting user confidentiality, maintaining data integrity, and guaranteeing absolute system availability are non-negotiable architectural mandates.

```
+-----------------------------------------------------------------------------------------+
|                               CLEFTPATH SECURITY PILLARS                                |
|                                                                                         |
|  1. MINIMAL PRIVILEGE     Zero trust boundary between frontend, backend, and database.  |
|  2. DATA ISOLATION        Strict row-level tenant authorization on every query.         |
|  3. ENCRYPTION EVERYWHERE TLS 1.3 in transit, AES-256-GCM at rest, S3 presigned blobs.  |
|  4. PHI REDACTION IN LOGS Automated log filters prevent clinical leaks in telemetry.    |
|  5. AI SAFETY GUARDS      Hardened prompt boundaries against jailbreaks and diagnosis.  |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Authentication & Credential Management

### 2.1 Password Hashing Specification
* **Algorithm:** Argon2id (Winner of the Password Hashing Competition)
* **Parameters:** `time_cost=3`, `memory_cost=65536` (64 MB), `parallelism=4`, `salt_len=16`, `hash_len=32`.
* **Policy:** Minimum 12 characters, requiring upper, lower, numeric, and symbol diversity. Checked against `HaveIBeenPwned` top 100k breached password dictionary.

### 2.2 Token & Session Architecture
* **Access Tokens:** JSON Web Tokens (JWT) signed with HMAC-SHA256 (or asymmetric RS256).
  * **Lifetime:** 15 minutes (`exp: now + 900s`).
  * **Payload Claims:** `sub` (User UUID), `role` (e.g. `caregiver`), `email`, `iat`, `exp`, `jti` (Token UUID).
  * **Transport:** Authorization Header `Bearer <token>` or `HttpOnly`, `SameSite=Strict`, `Secure` cookie.
* **Refresh Tokens:** High-entropy cryptographically random UUID strings stored hashed in the database.
  * **Lifetime:** 7 days (`exp: now + 604800s`).
  * **Rotation:** Every refresh token exchange issues a NEW refresh token and revokes the old one. If an invalidated refresh token is reused, the entire session family is revoked immediately (Token Theft Detection).

---

## 3. Role-Based Access Control (RBAC) & Multi-Tenant Isolation

### 3.1 Permission Matrix

| Resource / Capability | Caregiver (Parent) | Adult Patient | Clinician (Invited) | Moderator | System Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Manage Own Patients** | Full Control | Full Control (Self) | Read-Only (Invited) | No Access | No Access |
| **View Medical Documents**| Full Control | Full Control | Read-Only (Invited) | No Access | Audit Only |
| **Upload Speech/Audio** | Full Control | Full Control | No Access | No Access | No Access |
| **PathGuide AI Assistant**| Full Access | Full Access | Full Access | No Access | Metrics Only |
| **The Village: Post/Comment**| Yes | Yes | Yes | Yes | Yes |
| **The Village: Mod Queue**| No Access | No Access | No Access | Full Control | Full Control |
| **View Security Audit Logs**| No Access | No Access | No Access | No Access | Full Access |

### 3.2 Tenant Isolation & Insecure Direct Object Reference (IDOR) Prevention
To prevent horizontal privilege escalation where User A accesses Patient B's records:
```python
# app/api/deps.py - Enforced in FastAPI Dependency Injection
async def get_current_patient_with_access(
    patient_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Patient:
    patient = await patient_repo.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    
    # Enforce strict ownership / verified clinician delegation
    if patient.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        has_clinician_access = await delegation_repo.check_access(db, patient_id, current_user.id)
        if not has_clinician_access:
            raise HTTPException(status_code=403, detail="Access to this patient record is forbidden.")
    return patient
```

---

## 4. API & Network Security Guardrails

### 4.1 Rate Limiting (SlowAPI / Redis Token Bucket)
* `POST /api/v1/auth/login`: 5 requests / minute per IP.
* `POST /api/v1/auth/register`: 3 requests / hour per IP.
* `POST /api/v1/pathguide/*`: 20 requests / minute per user (prevents API cost exhaustion).
* Global API: 100 requests / minute per IP.

### 4.2 Cross-Origin Resource Sharing (CORS) & Headers
* **CORS Origin:** Strictly whitelisted (e.g. `http://localhost:5173` in dev, `https://app.cleftpath.org` in prod). `Allow-Credentials: true`.
* **Security Headers Injected by Middleware:**
  ```http
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Content-Security-Policy: default-src 'self'; img-src 'self' data: https:; script-src 'self'; style-src 'self' 'unsafe-inline';
  Referrer-Policy: strict-origin-when-cross-origin
  ```

### 4.3 Input Validation & XSS Prevention
* **Pydantic v2:** All incoming JSON payloads are strongly typed. Extraneous fields are stripped (`extra = "forbid"`).
* **Sanitization:** All markdown and free-text inputs for The Village and notes are sanitized through `bleach` and `DOMPurify` before storage and rendering, stripping `<script>`, `<iframe>`, `onload`, and javascript URIs.

---

## 5. File Storage & Upload Security

```
+-----------------------------------------------------------------------------------------+
|                               FILE UPLOAD SECURITY FLOW                                 |
|                                                                                         |
|  1. Client sends file metadata (MIME, size, filename) to backend.                      |
|  2. Backend validates MIME type whitelist and assigns random UUID key.                  |
|  3. Backend generates S3 presigned PUT URL expiring in 15 minutes.                      |
|  4. Client uploads encrypted bytes directly to S3.                                      |
|  5. Backend verifies magic numbers & runs anti-malware scan before enabling OCR.       |
+-----------------------------------------------------------------------------------------+
```

* **Whitelisted Extensions:** `.pdf`, `.png`, `.jpg`, `.jpeg`, `.wav`, `.webm`, `.mp3`.
* **Size Limits:** Max 25 MB for documents/PDFs, Max 50 MB for audio sessions.
* **Storage Isolation:** Real patient names or file names are never stored in S3 paths. Keys use the structure: `documents/{patient_uuid}/{file_uuid}.enc`.

---

## 6. Audit Logging & PHI Leakage Prevention

### 6.1 Structured JSON Audit Logs
All sensitive actions generate immutable records in the `audit_logs` table:
* Document downloads and OCR processing.
* Patient profile creations, updates, or deletions.
* User logins, password resets, and role changes.
* Full-data exports and account closure requests.

### 6.2 Zero-PHI Telemetry Rule
Logging frameworks (`structlog` / `loguru`) implement a custom filter interceptor that scrubs:
* Passwords and JWT tokens (`Authorization` header).
* Email addresses and phone numbers.
* Extracted medical OCR text and raw speech transcripts.
* Social Security Numbers / Medical Record Numbers.

---

## 7. AI Safety, Jailbreak Defense & Data Privacy

### 7.1 Data Privacy & Third-Party LLMs
* **Zero Model Training Clause:** CleftPath uses enterprise Google Gemini API tiers where customer data is **not** used to train foundation models.
* **Context De-identification:** When passing user context to PathGuide, the child's real legal name, birth hospital, and parent identity are stripped, passing only abstract clinical variables (e.g. *"Child (Age: 4 months, Bilateral Complete Cleft Lip and Palate)"*).

### 7.2 Prompt Injection Defense
* User messages are cleanly separated into delimited sections (`=== USER MESSAGE ===`) within system prompts.
* Output guard filters scan for unauthorized system prompt leakage or instructional hijacking attempts.
* Anti-Diagnosis classifier overrides model outputs that attempt to declare definitive diagnoses or drug dosages.

---

## 8. Data Subject Rights (GDPR & CCPA Compliance)

1. **Right to Access & Portability (`POST /api/v1/users/export-data`):**
   * Asynchronously packages all user data (profile, milestones, feeding logs, growth records, speech sessions, uploaded document metadata) into an encrypted ZIP file delivered via presigned download link.
2. **Right to Erasure / "Right to be Forgotten" (`DELETE /api/v1/users/account`):**
   * Executes a database cascade deletion across all associated patient records, feeding logs, documents, and chat messages.
   * Dispatches an S3 object deletion task to permanently delete stored files and audio recordings.
   * Anonymizes public Village posts by reassigning authorship to `[Deleted Account]`.

# Middleware Catalog — Industry Usage Guide

This document explains every middleware used in the demo: **why production apps use it**, **where it sits in the pipeline**, **how this repo configures it**, and **typical failure modes**.

Source of composition order: [`src/app.ts`](../src/app.ts).

---

## Pipeline order (why it matters)

| Order | Concern | Why here |
|------:|---------|----------|
| 1 | `trust proxy` | Must be first so `req.ip`, secure cookies, and rate limits see the real client behind Docker/LB |
| 2 | Request ID + ALS | Correlation available to every later layer and log line |
| 3 | Timeout / maintenance | Fail fast before expensive work |
| 4 | Helmet / CORS / compression / response-time | Security headers & transport concerns before body work |
| 5 | IP filter / slow-down / rate-limit | Cheap rejection of abuse |
| 6 | Body/cookie parsers | Populate `req.body` / cookies for downstream middleware |
| 7 | HPP / sanitize / content-type | Clean and constrain input before auth/business logic |
| 8 | Session → Passport | Session must exist before `passport.session()` can restore `req.user` |
| 9 | CSRF | Needs cookies/session; skips Bearer/API-key clients |
| 10 | Logging / metrics / audit | Observe authenticated identity when present |
| 11 | Routes | Business handlers + route-level middleware (RBAC, multer, idempotency, masking) |
| 12 | 404 + error handler | Always last |

---

## 1. Trust proxy (`app.set('trust proxy')`)

**Industry use:** Almost mandatory when Node sits behind NGINX, AWS ALB, Cloudflare, or Docker ingress.

**What it does:** Trusts `X-Forwarded-*` so Express computes correct `req.ip`, protocol (`https`), and host.

**Configured in:** [`src/app.ts`](../src/app.ts) via `TRUST_PROXY`.

**Failure mode:** Rate limiting / audit logs attribute traffic to the proxy IP; `secure` cookies may never set.

---

## 2. Request ID + AsyncLocalStorage

**Files:** [`src/middleware/request/requestContext.ts`](../src/middleware/request/requestContext.ts)

**Industry use:** Distributed tracing lite — every log line and error payload carries `x-request-id`.

**Behavior:**
- Honors inbound `x-request-id` or generates a UUID
- Echoes it on the response
- Stores `{ requestId, method, path, userId }` in `AsyncLocalStorage`

**Failure mode:** Missing IDs make incident correlation nearly impossible across services.

---

## 3. Request timeout

**File:** [`src/middleware/request/timeout.ts`](../src/middleware/request/timeout.ts)

**Industry use:** Protects worker event loops from hung handlers / slow dependencies.

**Config:** `REQUEST_TIMEOUT_MS` (default 15s). Demo: `GET /api/demo-errors/timeout`.

**Failure mode:** Too low → false 408s; too high → cascading resource exhaustion.

---

## 4. Maintenance mode

**File:** [`src/middleware/request/maintenance.ts`](../src/middleware/request/maintenance.ts)

**Industry use:** Deploy/incident kill-switch returning `503` while keeping `/api/health` alive for orchestrators.

**Config:** `MAINTENANCE_MODE=true`.

---

## 5. Helmet

**File:** [`src/middleware/security/helmet.ts`](../src/middleware/security/helmet.ts)

**Industry use:** Baseline HTTP hardening (CSP, `X-Content-Type-Options`, `Referrer-Policy`, frameguard, etc.).

**Failure mode:** Over-strict CSP can break legitimate frontends — tune directives per app.

---

## 6. CORS

**File:** [`src/middleware/security/cors.ts`](../src/middleware/security/cors.ts)

**Industry use:** Browser origin control for SPA/BFF architectures.

**Config:** `CORS_ORIGINS` allowlist, `credentials: true` for cookie sessions.

**Failure mode:** `*` + credentials is invalid; wrong origin → browser blocks, not always obvious in curl.

---

## 7. Compression

**Package:** `compression`

**Industry use:** Gzip/Brotli-style response compression for JSON/HTML to cut bandwidth.

**Failure mode:** Compressing already-compressed assets wastes CPU; usually fine for JSON APIs.

---

## 8. Response time

**Package:** `response-time`

**Industry use:** Adds `X-Response-Time` for quick latency debugging at the edge/app layer.

---

## 9. IP allow / deny lists

**File:** [`src/middleware/security/ipFilter.ts`](../src/middleware/security/ipFilter.ts)

**Industry use:** Admin planes, partner webhooks, emergency blocks.

**Config:** `IP_ALLOWLIST`, `IP_DENYLIST` (comma-separated). Empty = no filter.

---

## 10. Slow-down + rate limit

**File:** [`src/middleware/security/rateLimit.ts`](../src/middleware/security/rateLimit.ts)

**Industry use:**
- `express-slow-down` — progressive delay to absorb bursts
- `express-rate-limit` — hard `429` after budget
- Separate stricter bucket on `/api/auth/login` against credential stuffing

**Prod swap:** Redis store so limits are cluster-wide.

**Failure mode:** Without `trust proxy`, all users share the proxy IP and trip limits together.

---

## 11. Body parsers + size limits

**Packages:** `express.json`, `express.urlencoded`

**Industry use:** Parse payloads with explicit `BODY_LIMIT` (DoS control).

**Failure mode:** Huge bodies → `413` / memory pressure if limits are too high.

---

## 12. Cookie parser

**Package:** `cookie-parser`

**Industry use:** Reads cookies for sessions, CSRF double-submit, preferences.

**Depends on:** Signed cookie secret (`SESSION_SECRET`).

---

## 13. Method override

**Package:** `method-override`

**Industry use:** Legacy HTML forms that can only POST use `?_method=PUT`. Modern JSON APIs rarely need it; included because many enterprise Express apps still ship it.

---

## 14. HPP (HTTP Parameter Pollution)

**File:** [`src/middleware/security/hpp.ts`](../src/middleware/security/hpp.ts)

**Industry use:** Attackers send duplicate query keys (`?role=user&role=admin`) to confuse parsers. HPP keeps a single safe value (with optional whitelist for multi-value fields like `tags`).

---

## 15. Mongo sanitize

**File:** [`src/middleware/security/sanitize.ts`](../src/middleware/security/sanitize.ts)

**Industry use:** Strips `$gt`, `$ne`, `$where` style operators from input — classic NoSQL injection defense. Useful even if today you are on SQL but may serialize into document stores later.

---

## 16. XSS sanitization

**File:** [`src/middleware/security/sanitize.ts`](../src/middleware/security/sanitize.ts) (`xss`)

**Industry use:** Scrub HTML/script fragments from string fields. Complements Helmet CSP and output encoding.

**Failure mode:** Over-sanitizing can alter legitimate content (e.g. code samples).

---

## 17. Content-Type enforcement

**File:** [`src/middleware/security/contentType.ts`](../src/middleware/security/contentType.ts)

**Industry use:** Mutating JSON APIs reject unexpected media types (`415`). Upload routes are exempt for `multipart/form-data`.

---

## 18. Express session

**File:** [`src/middleware/auth/session.ts`](../src/middleware/auth/session.ts)

**Industry use:** Server-side session for browser logins (`connect.sid` httpOnly cookie).

**Demo store:** MemoryStore (process-local).

**Prod swap:** Redis / DynamoDB / Postgres session store. MemoryStore is not for multi-instance production.

---

## 19. Passport (core)

**File:** [`src/middleware/auth/passport.ts`](../src/middleware/auth/passport.ts)

### What Passport is

Passport is **not** an authentication protocol. It is a **middleware framework** that:

1. `passport.initialize()` — attaches Passport to the request
2. `passport.session()` — deserializes `req.user` from the session
3. Strategies — pluggable authenticators invoked as `passport.authenticate('name')`

### Why industry uses it

- One programming model for Local, JWT, OAuth, SAML, LDAP, etc.
- Keeps route handlers free of protocol details
- Mature ecosystem (`passport-local`, `passport-jwt`, `passport-google-oauth20`, `passport-saml`, …)

### Strategies in this demo

| Strategy | Package | Used for |
|----------|---------|----------|
| Local | `passport-local` | Email/password login → session |
| JWT | `passport-jwt` | `Authorization: Bearer` API access |

### Combined authenticate middleware

[`src/middleware/auth/authenticate.ts`](../src/middleware/auth/authenticate.ts) accepts **either** an existing session **or** a valid JWT — common in BFF + mobile API products.

### How OAuth would plug in (not live in this demo)

```ts
passport.use(new GoogleStrategy({ ... }, verifyCallback));
app.get('/auth/google', passport.authenticate('google', { scope: ['email'] }));
app.get('/auth/google/callback', passport.authenticate('google', { failureRedirect: '/login' }), issueSession);
```

Same `initialize` / `session` middleware — only the strategy and routes change.

### Failure modes

- Calling `passport.session()` before `express-session` → users never stick
- Forgetting `serializeUser` / `deserializeUser` → session auth broken
- JWT secret mismatch / expiry → `401 UNAUTHORIZED`

---

## 20. RBAC role guard

**File:** [`src/middleware/auth/roles.ts`](../src/middleware/auth/roles.ts)

**Industry use:** Enforce `admin` / `user` (or finer permissions) after identity is established.

---

## 21. API key middleware

**File:** [`src/middleware/auth/apiKey.ts`](../src/middleware/auth/apiKey.ts)

**Industry use:** Simple M2M auth for internal scrapers, webhooks, or service accounts (`x-api-key`). Often paired with network controls or mTLS in real deployments.

**Demo route:** `GET /api/metrics/json`.

---

## 22. HTTP Basic Auth

**File:** [`src/middleware/auth/basicAuth.ts`](../src/middleware/auth/basicAuth.ts)

**Industry use:** Still common for Prometheus scrape endpoints and operator tools.

**Demo route:** `GET /api/metrics`.

---

## 23. CSRF (double-submit cookie)

**File:** [`src/middleware/security/csrf.ts`](../src/middleware/security/csrf.ts)

**Industry use:** Protects cookie-authenticated browser POSTs from cross-site form attacks.

**Why not `csurf`:** The classic package is unmaintained; double-submit cookie is the modern pattern.

**Behavior in this app:**
- Issues `csrf_token` cookie + `x-csrf-token` header on requests
- Enforces header/cookie match on mutating requests **only when** `connect.sid` is present
- Skips Bearer JWT and `x-api-key` clients

**Failure mode:** SPA forgets to echo header → `403 CSRF_INVALID`.

---

## 24. Pino HTTP logging

**File:** [`src/middleware/logging/httpLogger.ts`](../src/middleware/logging/httpLogger.ts)

**Industry use:** Structured JSON access logs with levels and redaction.

**Why not Morgan?** Morgan is still widely taught, but pino-http is preferred in modern Node services for performance + JSON + field redaction. Morgan is a fine access-log alternative for simpler apps.

**Redaction:** Authorization, cookies, passwords, SSN, cards (see [`src/utils/logger.ts`](../src/utils/logger.ts)).

---

## 25. Metrics middleware

**File:** [`src/middleware/logging/httpLogger.ts`](../src/middleware/logging/httpLogger.ts) + [`src/services/metricsStore.ts`](../src/services/metricsStore.ts)

**Industry use:** Increment request/status counters for Prometheus-style scraping. Production often uses `prom-client` or OpenTelemetry instead of an in-memory map.

---

## 26. Audit logging

**File:** [`src/middleware/logging/audit.ts`](../src/middleware/logging/audit.ts)

**Industry use:** Immutable-ish trail of sensitive mutations (who/when/what route) for compliance (SOC2, PCI, HIPAA-adjacent workflows).

---

## 27. Response PII masking

**File:** [`src/middleware/privacy/responseMask.ts`](../src/middleware/privacy/responseMask.ts)

**Industry use:** Defense-in-depth so handlers can return full records internally while non-privileged clients receive masked email/phone/SSN/card.

**Demo:** `/api/customers*` — admins keep SSN last-4; others get fully masked SSN style.

---

## 28. Sensitive header stripping

**File:** [`src/middleware/privacy/stripHeaders.ts`](../src/middleware/privacy/stripHeaders.ts)

**Industry use:** Reduce server fingerprinting (`X-Powered-By`, `Server`).

---

## 29. Zod validation middleware

**File:** [`src/middleware/validation/validate.ts`](../src/middleware/validation/validate.ts)

**Industry use:** Schema-validate `body` / `query` / `params` before handlers run.

**Common alternative:** `express-validator` (chainable validators popular in many Express codebases). Zod is chosen here for TypeScript-first schemas shared with env config.

---

## 30. Idempotency-Key

**File:** [`src/middleware/request/idempotency.ts`](../src/middleware/request/idempotency.ts)

**Industry use:** Safe client retries for payments/orders — same key returns the original result instead of creating duplicates.

**Demo:** required on `POST /api/orders`.

**Prod swap:** Persist keys in Redis/DB with TTL.

---

## 31. Multer (multipart uploads)

**File:** [`src/middleware/upload/multer.ts`](../src/middleware/upload/multer.ts)

**Industry use:** Parse `multipart/form-data` for avatars, documents, KYC images with size + MIME allowlists.

**Demo:** `POST /api/uploads/avatar` field name `avatar`.

**Failure modes:** Wrong MIME → `INVALID_FILE_TYPE`; oversized → Multer `LIMIT_FILE_SIZE`.

---

## 32. express.static

**Industry use:** Serve public assets / uploaded files (or terminate static at CDN/NGINX in larger systems).

**Demo:** `/` → `public/`, `/uploads` → upload directory.

---

## 33. Async handler wrapper

**File:** [`src/middleware/errors/asyncHandler.ts`](../src/middleware/errors/asyncHandler.ts)

**Industry use:** Forward async rejections to Express error middleware. Alternative: `express-async-errors` monkey-patch.

---

## 34. 404 not-found middleware

**File:** [`src/middleware/errors/notFound.ts`](../src/middleware/errors/notFound.ts)

**Industry use:** Convert unmatched routes into a consistent JSON 404 **before** the error handler.

---

## 35. Centralized error handler

**File:** [`src/middleware/errors/errorHandler.ts`](../src/middleware/errors/errorHandler.ts)

**Industry use:** Single place to map domain errors, Zod, Multer, JWT, CSRF → stable `{ error: { code, message, requestId } }` bodies. Hides stacks in production.

---

## 36. Graceful shutdown / process handlers

**File:** [`src/server.ts`](../src/server.ts)

**Industry use:** On `SIGTERM` (Kubernetes rolling update), stop accepting connections, drain in-flight requests, then exit. Also log `unhandledRejection` / `uncaughtException`.

---

## Quick mapping: concern → middleware

| Concern | Middleware |
|---------|------------|
| AuthN (password) | Passport Local + session |
| AuthN (API token) | Passport JWT |
| AuthN (M2M) | API key / Basic |
| AuthZ | `requireRoles` |
| Security headers | Helmet |
| Browser origins | CORS |
| Abuse control | rate-limit + slow-down |
| Injection | mongo-sanitize + XSS + HPP |
| CSRF | double-submit cookie |
| Privacy | log redaction + response masking |
| Observability | pino-http + metrics + audit + request id |
| Uploads | multer |
| Validation | Zod |
| Reliability | timeout + maintenance + graceful shutdown |
| Retries | Idempotency-Key |

# Node.js Middleware Demo

Production-style **Express + TypeScript** API that demonstrates industry middleware for security, Passport authentication, sessions/CSRF, logging, PII masking, validation, uploads, rate limiting, and centralized error handling — packaged with Docker.

Deep per-middleware reference: [`docs/MIDDLEWARE.md`](docs/MIDDLEWARE.md).

## Middleware pipeline

```
trust proxy
  → requestId + AsyncLocalStorage
  → timeout / maintenance
  → helmet / cors / compression / response-time
  → IP filter / slow-down / rate-limit
  → json + urlencoded + cookie-parser + method-override
  → hpp / mongo-sanitize / xss / content-type
  → express-session
  → passport.initialize + passport.session
  → CSRF issuer + CSRF protection
  → pino-http + metrics + audit
  → static / routes (auth, JWT/session, multer, RBAC, idempotency, masking)
  → 404 + centralized error handler
```

## Prerequisites

- Node.js 20+
- Docker & Docker Compose (recommended)

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

| Endpoint | URL |
|----------|-----|
| Health | http://localhost:3000/api/health |
| Static page | http://localhost:3000/ |
| Metrics (Basic) | http://localhost:3000/api/metrics |

## Local development

```bash
cp .env.example .env
npm install
npm run dev
```

Production-like local run:

```bash
npm run build
npm run start:prod
```

## Demo credentials

| Email | Password | Role |
|-------|----------|------|
| admin@demo.local | password123 | admin |
| user@demo.local | password123 | user |

| Secret | Value |
|--------|-------|
| API key (`x-api-key`) | `demo-service-api-key` |
| Metrics basic auth | `metrics` / `metrics-secret` |

## API cookbook

### Login (Passport Local → session cookie + JWT)

```bash
curl -i -c cookies.txt -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@demo.local","password":"password123"}'
```

Copy `accessToken` from the JSON body.

### Current user (JWT)

```bash
TOKEN="<access_token>"

curl -s http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Current user (session cookie)

```bash
curl -s -b cookies.txt http://localhost:3000/api/auth/me | jq
```

### List customers (PII masking)

Non-admin responses mask email/phone/SSN/card. Admin still receives masked values with SSN last-4 retained by the privacy middleware.

```bash
curl -s http://localhost:3000/api/customers \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Create order (idempotency)

```bash
curl -s -X POST http://localhost:3000/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: demo-order-001" \
  -d '{"customerId":"c-1","sku":"SKU-42","quantity":2,"amountCents":1999}' | jq
```

Replay the same request with the same `Idempotency-Key` — you get the same order id.

### Upload avatar (multer)

```bash
curl -s -X POST http://localhost:3000/api/uploads/avatar \
  -H "Authorization: Bearer $TOKEN" \
  -F "avatar=@./public/index.html;type=image/png"
```

Use a real PNG/JPEG/WebP file for a successful upload; wrong MIME types return `INVALID_FILE_TYPE`.

### CSRF (cookie-session mutating requests)

```bash
# 1) get token (also set as csrf_token cookie)
curl -s -c cookies.txt -b cookies.txt http://localhost:3000/api/auth/csrf | jq

# 2) after login, mutating calls that rely on the session cookie must echo x-csrf-token
CSRF=$(jq -r .csrfToken <<< "$(curl -s -c cookies.txt -b cookies.txt http://localhost:3000/api/auth/csrf)")

curl -s -b cookies.txt -X POST http://localhost:3000/api/customers \
  -H "Content-Type: application/json" \
  -H "x-csrf-token: $CSRF" \
  -d '{"name":"Pat","email":"pat@example.com","phone":"+15550199","ssn":"111-22-3333","cardNumber":"4111111111111111"}' | jq
```

Bearer JWT requests skip CSRF checks (not cookie-auth CSRF vulnerable in the classic sense).

### Metrics

```bash
curl -s -u metrics:metrics-secret http://localhost:3000/api/metrics
curl -s http://localhost:3000/api/metrics/json -H "x-api-key: demo-service-api-key" | jq
```

### Error demos

```bash
curl -s http://localhost:3000/api/demo-errors/app-error | jq
curl -s http://localhost:3000/api/demo-errors/unhandled | jq
```

## Project layout

```
src/
  app.ts                 # middleware composition order
  server.ts              # listen + graceful shutdown
  config/env.ts          # zod-validated environment
  middleware/            # security, auth, request, logging, privacy, validation, upload, errors
  routes/                # auth, customers, orders, uploads, health, metrics, demo-errors
  services/              # in-memory stores + seed users/customers
docs/MIDDLEWARE.md       # detailed middleware catalog
Dockerfile / docker-compose.yml
```

## Notes for production swaps

- Replace `MemoryStore` sessions with Redis (`connect-redis`)
- Back rate-limit / idempotency stores with Redis
- Terminate TLS at a reverse proxy and keep `TRUST_PROXY=true`
- Ship pino logs to your log platform; scrape `/api/metrics` or use OpenTelemetry
- Add real OAuth strategies (`passport-google-oauth20`, etc.) beside Local/JWT

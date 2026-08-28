# NestJS 11 Full-Stack Demo

Task management API demonstrating NestJS 11 features: standard CLI scaffolding, full HTTP request lifecycle, JWT authentication, JSON logging, Swagger, GraphQL, Kafka hybrid microservice, SQLite persistence, and Jest testing.

## Request lifecycle (REST)

`POST /api/tasks` exercises every layer in order:

```
Middleware → Guards → Interceptors (pre) → Pipes → Route Handler → Interceptors (post) → Exception Filter → Response
```

Each layer logs structured JSON with `layer` and `requestId` fields.

## Prerequisites

- Node.js 20+
- Docker & Docker Compose (for Kafka)

## Quick start

```bash
# 1. Start Kafka (and Kafka UI on :8080)
npm run docker:up

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env

# 4. Seed SQLite database
npm run seed

# 5. Start the app
npm run start:dev
```

| Endpoint | URL |
|----------|-----|
| Health | http://localhost:3000/api/health |
| Swagger | http://localhost:3000/docs |
| GraphQL | http://localhost:3000/graphql |
| Kafka UI | http://localhost:8080 |

## Demo credentials

| Email | Password | Role |
|-------|----------|------|
| admin@demo.local | password123 | admin |
| user@demo.local | password123 | user |

## API examples

### Login

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@demo.local","password":"password123"}'
```

### Create task (full pipeline + Kafka emit)

```bash
TOKEN="<access_token from login>"

curl -X POST http://localhost:3000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"New task","description":"Created via REST"}'
```

Watch JSON logs for `middleware`, `guard`, `interceptor`, `service`, and `kafka-consumer` layers.

### GraphQL

Open http://localhost:3000/graphql and set HTTP Headers:

```json
{ "Authorization": "Bearer <token>" }
```

```graphql
query {
  tasks {
    id
    title
    status
  }
}

mutation {
  createTask(input: { title: "GraphQL task" }) {
    id
    title
  }
}
```

## Project structure

```
src/
  main.ts                 # Bootstrap: JSON logger, helmet, CORS, Swagger, Kafka hybrid
  app.module.ts           # Root module + RequestIdMiddleware
  common/                 # Middleware, guards, interceptors, filters, decorators
  auth/                   # JWT + Passport local strategy
  users/                  # User entity & service
  tasks/                  # REST CRUD + Kafka emit on create
  kafka/                  # Kafka client + @EventPattern consumer + audit entity
  graphql-api/            # Code-first GraphQL resolvers
scripts/
  schema.sql              # SQLite DDL
  seed.sql                # Sample SQL data
  seed.ts                 # Programmatic seed (npm run seed)
docker/
  kafka-init.sh           # Creates task.created topic
```

## Database

- **Runtime**: TypeORM with `better-sqlite3` (`./data/app.sqlite`)
- **Schema**: [`scripts/schema.sql`](scripts/schema.sql)
- **Seed**: `npm run seed` or [`scripts/seed.sql`](scripts/seed.sql)

## Kafka

- Hybrid app: HTTP + GraphQL on port 3000, Kafka consumer in same process
- `TasksService.create` emits `task.created` events
- `TaskEventsController` consumes events and writes to `task_audit` table
- Topic `task.created` created by `docker/kafka-init.sh`

## Testing

```bash
npm test          # Unit tests (includes TasksService sample)
npm run test:e2e  # E2E health check
```

## Security

- `helmet` for HTTP security headers
- CORS configured via `CORS_ORIGIN`
- JWT bearer auth on protected routes
- `RolesGuard` for admin-only delete

## Production notes

- Set `NODE_ENV=production` and disable TypeORM `synchronize`; use migrations instead
- Use a strong `JWT_SECRET`
- Replace SQLite with PostgreSQL for production workloads

## CI/CD

A full GitHub Actions → EKS → ECR pipeline is available for this project. See [docs/CI-CD-SETUP.md](docs/CI-CD-SETUP.md) for provisioning AWS, configuring GitHub, and running the pipeline.

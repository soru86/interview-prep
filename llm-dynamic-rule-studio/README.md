# LLM Dynamic Rule Studio

React rule editor + chatbot that generates business rules with nested AND/OR conditions using **DeepSeek R1** via **Ollama**. Generated fields can be added to the main rule screen with one click.

## Stack

- **Frontend:** React + Vite + TypeScript + Zustand
- **Backend:** FastAPI + SQLAlchemy (async)
- **Database:** PostgreSQL (JSONB condition trees)
- **LLM:** Ollama `deepseek-r1:1.5b` (CPU-friendly DeepSeek R1; override with `OLLAMA_MODEL`)

## Quick start (Docker)

Requires Docker Desktop (or another Docker daemon) running.

```bash
cp .env.example .env
docker compose up --build
```

**Important:** Do not re-run `docker compose up --build` while a chat is generating — rebuilds restart containers and kill in-flight Ollama work.

Services:

| Service | URL |
|---------|-----|
| Web UI | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| Ollama | http://localhost:11434 |

`ollama-init` pulls `deepseek-r1:1.5b` on first start.

## How chat works

1. UI `POST /api/chat/sessions/{id}/messages` → **202 Accepted** immediately (user + pending assistant rows saved).
2. API runs Ollama in a **background task**.
3. UI polls `GET /api/chat/messages/{id}` every 2s until `status` is `complete` or `error`.
4. Click **Add to Rule Screen**, then **Save Rule**.

This avoids multi-minute browser→nginx→API hangs that caused “Failed to fetch” / 504 / connection drops.

## Local development

### 1. Infrastructure

```bash
docker compose up postgres ollama ollama-init -d
```

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (Vite proxies `/api` to the backend).

## Usage

1. Open the Rule Screen (left).
2. In the chatbot (right), describe a rule, e.g.  
   `VIP customers with cart total over 500 OR loyalty tier gold`
3. Wait for the assistant message to leave “generating…” status.
4. Click **Add to Rule Screen**, then **Save Rule**.

## Optional: larger R1 model

```bash
docker compose exec ollama ollama pull deepseek-r1:8b
# set OLLAMA_MODEL=deepseek-r1:8b in docker-compose / .env and recreate api
```

## API overview

- `GET/POST /api/rules`, `GET/PUT/DELETE /api/rules/{id}`
- `GET/POST /api/fields`
- `POST /api/chat/sessions`
- `POST /api/chat/sessions/{id}/messages` → 202 + pending assistant message
- `GET /api/chat/messages/{id}` → poll until complete/error
- `GET /api/health`

## Project layout

```
llm-dynamic-rule-studio/
  backend/          FastAPI app
  frontend/         React SPA
  docker-compose.yml
  .env.example
```

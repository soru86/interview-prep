# Java RAG Demo v2 (Fully Offline: Ollama + DeepSeek R1 + Qdrant)

Spring Boot lab that implements a production-style **RAG** pipeline with a **100% local, offline** LLM stack:

- **DeepSeek R1** chat model (`deepseek-r1:1.5b`) served by **Ollama** — no API keys, no cloud calls
- **nomic-embed-text** embeddings (768-dim, verified against the live model at startup)
- **Qdrant** vector store (`me_war_docs_v2` + `chat_memory_v2`)
- **Short-term** conversation memory (message window per session)
- **Long-term** memory (embedded turn summaries in Qdrant, filtered by session)
- PDF corpus ingestion with recursive chunking and per-chunk metadata
- Web chat UI with **SSE token streaming**, a collapsible **reasoning** panel
  (DeepSeek R1's `<think>` output), and source previews
- Everything runs in **Docker** via a single `docker compose up`

Corpus topic: Middle East war updates **28 Feb 2026 – 13 Jul 2026** (generated PDF).

## Quick start (all-in-Docker)

```bash
cd java-rag-demo-v2
docker compose up --build
```

What happens:

1. `qdrant` starts and passes its healthcheck.
2. `ollama` starts; `ollama-init` pulls `deepseek-r1:1.5b` (~1.1 GB) and
   `nomic-embed-text` (~274 MB) into a named volume (first run only), then exits.
3. `app` builds (multi-stage Maven image), waits for both, verifies the embedding
   dimension against the live model, generates the corpus PDF if missing, and
   auto-ingests it into Qdrant.

Then open [http://localhost:8080](http://localhost:8080).

> First model responses can take tens of seconds on CPU-only machines while the
> model warms up. `deepseek-r1:1.5b` is chosen to keep RAM usage low (~2-3 GB);
> for better answers set `OLLAMA_CHAT_MODEL=deepseek-r1:8b` in `.env`
> and update the pull command in `docker-compose.yml` (needs ~8+ GB RAM).

## Quick start (app on host, infra in Docker)

```bash
cd java-rag-demo-v2

# 1) Start Qdrant + Ollama only
docker compose up -d qdrant ollama ollama-init

# 2) Optional: tune config
cp .env.example .env
export $(grep -v '^#' .env | xargs)

# 3) Run the app (generates + ingests corpus PDF on startup)
mvn spring-boot:run
```

## Useful endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Streaming chat UI |
| POST | `/api/chat` | SSE chat (`X-Session-Id` optional) |
| POST | `/api/ingest` | Re-ingest the PDF corpus |
| GET | `/api/health` | Liveness |
| GET | `/actuator/health` | Spring Actuator health |

### Example chat request (SSE)

```bash
curl -N -X POST http://localhost:8080/api/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Session-Id: demo-session-1' \
  -d '{"message":"What happened on 28 February 2026?"}'
```

SSE event names: `session`, `sources`, `thinking`, `token`, `done`, `error`.
`thinking` carries DeepSeek R1's chain-of-thought (from `<think>...</think>`);
`token` carries only the final answer, which is also what gets persisted to memory.

## Configuration

All tunables are env-driven (see `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_CHAT_MODEL` | `deepseek-r1:1.5b` | Streaming chat model |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model |
| `OLLAMA_EMBEDDING_DIMENSIONS` | `768` | Expected vector size (verified at startup) |
| `OLLAMA_TIMEOUT_SECONDS` | `300` | Chat/embedding call timeout |
| `OLLAMA_TEMPERATURE` | `0.6` | R1-recommended sampling temperature |
| `QDRANT_HOST` / `QDRANT_GRPC_PORT` | `localhost` / `6334` | Qdrant gRPC |
| `RAG_TOP_K` | `5` | Retrieved chunks |
| `RAG_MIN_SCORE` | `0.60` | Cosine similarity floor |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | `500` / `50` | Splitter settings |
| `RAG_AUTO_INGEST` | `true` | Ingest PDF on startup |
| `SHORT_TERM_MAX_MESSAGES` | `20` | In-memory turn window |
| `LONG_TERM_TOP_K` / `LONG_TERM_MIN_SCORE` | `3` / `0.55` | Long-term memory retrieval |

## Architecture

```
PDF → chunk + metadata → nomic-embed-text (Ollama) → Qdrant (me_war_docs_v2)
User question → embed query → retrieve docs + long-term memories → prompt
             → short-term chat history → DeepSeek R1 stream (Ollama)
             → SSE: thinking (reasoning) + token (answer) → UI
             → append turn → embed summary → Qdrant (chat_memory_v2)
```

### RAG practices included

- Same embedding model for ingest and query
- Embedding dimension **verified against the live model at startup** (fail fast on mismatch)
- Metadata on chunks (`source`, `corpus`, `section_hint`) surfaced as source previews
- Similarity `minScore` gate to reduce weak retrieval
- Explicit grounded system prompt with refusal when context is thin
- Reasoning (`<think>`) separated from the answer; only the answer is persisted to memory
- Separate collections for knowledge vs conversational long-term memory
- Config via environment variables only; no secrets required at all (fully offline)

## Project layout

```
java-rag-demo-v2/
  docker-compose.yml            # qdrant + ollama + ollama-init + app
  Dockerfile                    # multi-stage Maven build
  data/corpus/                  # generated PDF output (host runs)
  src/main/java/com/interviewprep/ragdemov2/
    config/     # AppProperties, Ollama + Qdrant beans
    pdf/        # Corpus PDF generator (28 Feb - 13 Jul 2026)
    ingest/     # Dimension probe, chunk, embed, upsert
    memory/     # Short-term window + long-term Qdrant memory
    rag/        # Retrieval + grounded prompt assembly
    chat/       # SSE controller, streaming service, think-tag splitter
  src/main/resources/static/index.html
```

## Tests

```bash
mvn test
```

Covers: PDF generation, section-hint inference, think-tag stream splitting
(including tags split across token boundaries).

## Notes

- Regenerate the corpus manually: `mvn -q exec:java` (writes `data/corpus/middle-east-war-updates-2026.pdf`).
- After changing the embedding model, restart with auto-ingest (or `POST /api/ingest`) so
  collections are recreated at the new vector size — the startup probe enforces this.
- Long-term memory is session-scoped via payload `sessionId`.
- Qdrant dashboard: [http://localhost:6333/dashboard](http://localhost:6333/dashboard).
- This lab intentionally omits auth, hybrid BM25, and rerankers — natural next steps for production.

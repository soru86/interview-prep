# Java RAG Demo (LangChain4j + Qdrant)

Spring Boot lab that implements a production-style **RAG** pipeline:

- PDF corpus ingestion with recursive chunking and **Google** embeddings
- **Qdrant** vector store (`me_war_docs` + `chat_memory`)
- **Short-term** conversation memory (message window per session)
- **Long-term** memory (embedded summaries in Qdrant, filtered by session)
- Configurable **Google AI** API key and Gemini models
- Simple web chat UI with **SSE token streaming** and source previews

Corpus topic: Middle East war updates **28 Feb 2026 – 12 Jul 2026**.

## Prerequisites

- Java 21+
- Maven 3.9+
- Docker (for Qdrant)
- A Google AI Studio API key ([create one](https://aistudio.google.com/apikey))

## Quick start

```bash
cd java-rag-demo

# 1) Start Qdrant
docker compose up -d

# 2) Configure secrets
cp .env.example .env
# edit .env and set GOOGLE_AI_API_KEY

export $(grep -v '^#' .env | xargs)

# 3) Generate corpus PDF (also auto-generated on first ingest if missing)
mvn -q exec:java -Dexec.mainClass=com.interviewprep.ragdemo.pdf.CorpusPdfGenerator

# 4) Run the app (auto-ingests PDF into Qdrant on startup)
mvn spring-boot:run
```

Open [http://localhost:8080](http://localhost:8080).

### Useful endpoints

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

SSE event names: `session`, `sources`, `token`, `done`, `error`.

## Configuration

All secrets and tunables are env-driven (see `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOOGLE_AI_API_KEY` | _(required)_ | Google AI Studio API key |
| `GOOGLE_CHAT_MODEL` | `gemini-2.0-flash` | Streaming Gemini chat model |
| `GOOGLE_EMBEDDING_MODEL` | `gemini-embedding-001` | Embedding model |
| `GOOGLE_EMBEDDING_DIMENSIONS` | `768` | Qdrant vector size |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_GRPC_PORT` | `6334` | Qdrant gRPC port |
| `RAG_TOP_K` | `5` | Retrieved chunks |
| `RAG_MIN_SCORE` | `0.65` | Cosine similarity floor |
| `RAG_CHUNK_SIZE` | `500` | Approx chunk size (chars/tokens splitter) |
| `RAG_CHUNK_OVERLAP` | `50` | Chunk overlap |
| `RAG_AUTO_INGEST` | `true` | Ingest PDF on startup |
| `SHORT_TERM_MAX_MESSAGES` | `20` | In-memory turn window |

## Architecture

```
PDF → chunk + metadata → Google embeddings → Qdrant (me_war_docs)
User question → retrieve docs + long-term memories → prompt
             → short-term chat history → Gemini stream → SSE UI
             → append turn → embed summary → Qdrant (chat_memory)
```

### RAG practices included

- Same embedding model for ingest and query
- Metadata on chunks (`source`, corpus id)
- Similarity `minScore` gate to reduce weak retrieval
- Explicit grounded system prompt with refusal when context is thin
- Source events returned to the client for transparency
- Separate collections for knowledge vs conversational long-term memory
- Secrets via environment variables only

## Project layout

```
java-rag-demo/
  docker-compose.yml
  data/corpus/middle-east-war-updates-2026.pdf
  src/main/java/com/interviewprep/ragdemo/
    config/     # Google Gemini + Qdrant beans, properties
    pdf/        # Corpus PDF generator
    ingest/     # Chunk, embed, upsert
    memory/     # Short-term + long-term
    rag/        # Retrieval + prompt assembly
    chat/       # REST + SSE streaming
  src/main/resources/static/index.html
```

## Notes

- First startup recreates/loads the docs collection; ensure Qdrant is healthy (`http://localhost:6333/dashboard`).
- After changing embedding model/dimensions, re-ingest (`POST /api/ingest` or restart with auto-ingest) so Qdrant collections match the new vector size.
- Long-term memory is session-scoped via payload `sessionId`.
- This lab intentionally omits auth, hybrid BM25, and rerankers — natural next steps for production.

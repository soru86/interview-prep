# Recruiter Email AI Agent

Production-oriented Python agent that:

1. Reads recruiter emails from a Gmail label (`Recruiters`)
2. Extracts job details using **DeepSeek R1** via **Ollama** (Docker)
3. Matches each role against your resume
4. Creates **Gmail drafts** (with CV attached) when match score ≥ 70%
5. Sends a **WhatsApp notification** when a draft is created
6. Maintains an **Excel tracker** of all recruiter interactions

---

## Architecture

```
Gmail (label: Recruiters)
    → Recruiter Filter (heuristics + LLM)
    → Job Extractor (Ollama / DeepSeek R1)
    → Resume Matcher (Ollama / DeepSeek R1)
    → Reply Drafter → Gmail Draft + CV attachment
    → WhatsApp notification (Meta Business Cloud API)
    → Excel tracker + SQLite state DB
```

---

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Google Cloud project with Gmail API enabled
- Meta WhatsApp Business Cloud API account (production messaging)
- Your resume (PDF or DOCX) in `data/resume/`

---

## Quick Start

### 1. Start Ollama with DeepSeek R1

```bash
cd ai-agent-demo
docker compose up -d ollama
docker compose run --rm ollama-init   # pulls deepseek-r1:8b (may take several minutes)
```

Verify:

```bash
curl http://localhost:11434/api/tags
```

### 2. Install the agent

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Description |
|----------|-------------|
| `GMAIL_CREDENTIALS_PATH` | Path to OAuth `credentials.json` from Google Cloud |
| `GMAIL_RECRUITER_LABEL` | Gmail label name (default: `Recruiters`) |
| `META_WHATSAPP_ACCESS_TOKEN` | Permanent token from Meta App Dashboard |
| `META_WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID from Meta |
| `WHATSAPP_TO` | Your number, digits only (default: `971568896895`) |
| `META_WHATSAPP_MESSAGE_MODE` | `template` (production) or `text` (24h window only) |
| `META_WHATSAPP_TEMPLATE_NAME` | Approved template name (default: `recruiter_draft_alert`) |
| `MATCH_THRESHOLD` | Minimum match score to draft reply (default: `70`) |

### 4. Gmail OAuth setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Gmail API**
3. Create **OAuth 2.0 Desktop** credentials → download as `credentials.json`
4. Place `credentials.json` in the project root
5. Create a Gmail label named **Recruiters** and apply it to recruiter emails

On first run, a browser window opens for OAuth consent. A `token.json` is saved for subsequent runs.

### 5. Add your resume

```bash
cp /path/to/your/resume.pdf data/resume/
```

Only one resume is used (most recently modified file in the folder).

### 6. Meta WhatsApp Business API setup (production)

Yes — Meta WhatsApp Cloud API supports **real production message delivery** to your phone (+971568896895), unlike sandbox-only providers.

**Two message modes:**

| Mode | When to use |
|------|-------------|
| `template` (default) | **Production outbound alerts** — requires a pre-approved template in Meta Business Manager |
| `text` | Free-form messages — only works within **24 hours** after you last messaged your business number |

**Setup steps:**

1. Create a [Meta Business](https://business.facebook.com/) account
2. Go to [Meta for Developers](https://developers.facebook.com/) → Create App → **Business** type
3. Add the **WhatsApp** product → complete Business verification if prompted
4. In **WhatsApp → API Setup**, note:
   - **Phone number ID** → `META_WHATSAPP_PHONE_NUMBER_ID`
   - **Temporary access token** (for testing) or create a **System User** permanent token → `META_WHATSAPP_ACCESS_TOKEN`
5. Create and approve a message template in **WhatsApp Manager → Message Templates**:

   - **Name:** `recruiter_draft_alert`
   - **Category:** Utility
   - **Language:** English
   - **Body:**
     ```
     Recruiter Agent: draft created for {{1}} at {{2}}.
     Role: {{3}} | Match: {{4}}% | Subject: {{5}}.
     Review the draft in Gmail before sending.
     ```

6. Add your personal number as a test recipient (during development) or ensure your number has opted in (production)
7. Set values in `.env`:

```env
WHATSAPP_PROVIDER=meta
WHATSAPP_TO=971568896895
META_WHATSAPP_ACCESS_TOKEN=your-permanent-token
META_WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
META_WHATSAPP_MESSAGE_MODE=template
META_WHATSAPP_TEMPLATE_NAME=recruiter_draft_alert
```

**Optional — Twilio alternative:** set `WHATSAPP_PROVIDER=twilio` and install with `pip install -e ".[twilio,dev]"`.

### 7. Run the agent

```bash
# Check configuration
recruiter-agent status

# Process emails (draft-only, never auto-sends)
recruiter-agent run

# Limit batch size
recruiter-agent run --max-emails 20
```

---

## Output

| Artifact | Location |
|----------|----------|
| Excel tracker | `data/tracker/recruiter_tracker.xlsx` |
| Processed email state | `data/state/agent.db` |
| Gmail drafts | Your Gmail Drafts folder |

### Excel columns

- Recruiter Name
- Contact Email
- Contact Phone
- Company
- Role Applied For
- Match Score
- Date of First Reply
- Email Subject
- Status (`drafted` / `skipped` / `review` / `error`)
- Message ID

---

## Scheduling (cron example)

Run every hour:

```cron
0 * * * * cd /path/to/ai-agent-demo && .venv/bin/recruiter-agent run >> logs/agent.log 2>&1
```

---

## Safety defaults

- **Draft only** — replies are never auto-sent (`AUTO_SEND=false` is enforced)
- **Idempotent** — processed message IDs are stored in SQLite; re-runs skip already-handled emails
- **Dry run** — set `DRY_RUN=true` to test LLM matching without creating drafts

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Gmail label 'Recruiters' not found` | Create the label in Gmail and apply it to emails |
| Ollama timeout | Increase `OLLAMA_TIMEOUT_SECONDS`; use a smaller model tag if needed |
| Empty LLM JSON | DeepSeek R1 may emit `` blocks — the parser strips these automatically |
| WhatsApp not sent | Check Meta token, phone number ID, template approval status, and that `WHATSAPP_TO` is digits-only |
| No resume found | Add a `.pdf` or `.docx` file to `data/resume/` |

---

## Development

```bash
pytest
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed flow and sequence diagrams.

---

## Project structure

```
src/recruiter_agent/
├── main.py                 # CLI entry point
├── config.py               # Settings (Pydantic)
├── models/                 # Domain models
├── providers/
│   ├── email/gmail.py      # Gmail fetch + draft creation
│   └── llm/ollama.py       # DeepSeek R1 via Ollama
├── pipeline/               # Processing stages
├── storage/                # SQLite + Excel
├── notifications/          # WhatsApp via Meta Cloud API (Twilio optional)
└── utils/                  # Resume parsing, logging
```

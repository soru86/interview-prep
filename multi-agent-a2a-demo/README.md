# Multi-Agent A2A Mailbox-to-WhatsApp Demo

Two agents talk over the [Agent2Agent (A2A)](https://a2a-protocol.org/) protocol:

1. **Mailbox Agent** reads IMAP mail (credentials in `config/config.yaml`).
2. **WhatsApp Agent** sends a notification with sender, subject, and a **TOP PRIORITY** flag when the mail contains `job`, `opportunity`, `opening`, or `position`.

Each agent uses MCP tools (email IMAP + WhatsApp send). Inference uses **DeepSeek R1 1.5B** via **Ollama in Docker**. All agent, A2A, MCP, IMAP, LLM, and WhatsApp activity is logged to the console and `logs/agents.log`.

```
IMAP mailbox
    → email-mcp (list_unread / fetch_message)
    → Mailbox Agent (DeepSeek extract + keyword priority)
    → A2A JSON-RPC → WhatsApp Agent
    → whatsapp-mcp (send_notification)
    → Meta Cloud API or Twilio → your WhatsApp number
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- IMAP mailbox (Outlook.com uses Microsoft OAuth2 — password IMAP is blocked. Gmail with an app password is commented in the config example.)
- Meta WhatsApp Cloud API **or** Twilio WhatsApp

## Quick start

### 1. Start Ollama and pull DeepSeek R1 1.5B

```bash
cd multi-agent-a2a-demo
docker compose up -d ollama
docker compose run --rm ollama-init
curl http://localhost:11434/api/tags
```

### 2. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Twilio extra (only if you use Twilio): `pip install -e ".[twilio,dev]"`

### 3. Configure

```bash
cp config/config.example.yaml config/config.yaml
```

Edit `config/config.yaml`:

| Key | Purpose |
|-----|---------|
| `mailbox.host/username` | Outlook.com: `outlook.office365.com` + your address. Gmail is commented in the example. |
| `mailbox.auth` | `oauth2` for Outlook.com. `password` for Gmail app passwords. |
| `mailbox.oauth_client_id` | Entra **Application (client) ID** (required for Outlook.com) |
| `whatsapp.to` | Destination number, digits only (e.g. `971568896895`) |
| `whatsapp.provider` | `meta` (default) or `twilio` |
| `whatsapp.meta.*` | Meta access token + phone number ID |
| `whatsapp.twilio.*` | Twilio SID, auth token, from-number |
| `dry_run` | `true` logs the WhatsApp payload and does not send |

Secrets can also be supplied as env vars (`MAILBOX_OAUTH_CLIENT_ID`, `WHATSAPP_TO`, `META_WHATSAPP_ACCESS_TOKEN`, …). Env wins over YAML.

### Outlook.com OAuth (required)

Microsoft blocked username/password IMAP. Use the current [Entra app registration](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) plus [IMAP OAuth](https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth) (device-code flow). You do **not** add `IMAP.AccessAsUser.All` under Microsoft Graph, and you usually will **not** see Office 365 Exchange Online in a personal-account tenant.

1. In Outlook on the web, enable IMAP: [outlook.live.com](https://outlook.live.com) → Settings → Mail → Forwarding and IMAP → **Let devices and apps use IMAP**.
2. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com) (create a free Azure subscription if you do not have a tenant).
3. **Entra ID** → **App registrations** → **New registration**.
4. Name: `a2a-mail-notify`.
5. **Supported account types**: **Personal accounts only** (Outlook.com / Hotmail / Live).
6. Leave **Redirect URI** empty (device-code login does not need one). Select **Register**.
7. Copy **Application (client) ID** from Overview into `mailbox.oauth_client_id`.
8. **Manage** → **Authentication** → **Advanced settings** → **Allow public client flows** → **Yes** → Save.
9. Keep `mailbox.oauth_tenant: consumers` and `mailbox.auth: oauth2`.
10. Run:

```bash
a2a-mail-notify login
a2a-mail-notify status
a2a-mail-notify run
```

`login` requests the official IMAP scope `https://outlook.office.com/IMAP.AccessAsUser.All` at token time (MSAL adds the refresh-token scope itself). Complete the URL/code in the browser; the token is stored in `data/state/msal_token.json`. Run `login` by itself — do not chain it with `status` or `run` on the same paste.

Skip **API permissions → Office 365 Exchange Online → IMAP.AccessAsApp**. That is the work/school *application* (daemon) path and needs an Exchange Online tenant. It is not how personal Outlook.com IMAP OAuth works.

### 4. Run

```bash
a2a-mail-notify login
a2a-mail-notify status
a2a-mail-notify run
a2a-mail-notify run --once
a2a-mail-notify run --max-emails 5
```

`run` keeps polling the mailbox every `poll_interval_seconds` (default **5 seconds**) and sends each new message to the WhatsApp agent over A2A. Already-notified Message-IDs are skipped. Use `--once` for a single check. Agent cards only come up after `run` starts the two A2A servers (mailbox `:9001`, WhatsApp `:9002`).

## WhatsApp providers

**Meta (default)** — production outbound messages need an approved template. Free-form `text` only works inside the 24-hour customer-care window after the user messages your business number.

Suggested template name `email_alert`:

```
{{1}} From: {{2}} Subject: {{3}}
```

Example body: `TOP PRIORITY From: Ada <ada@x.com> Subject: Job opening`

**Twilio** — set `whatsapp.provider: twilio` and fill `twilio.account_sid`, `auth_token`, `from_number`.

## How the agents talk (A2A)

- Each agent publishes an Agent Card (`/.well-known/agent-card.json`) with its skills.
- Transport is JSON-RPC 2.0 over HTTP via the official `a2a-sdk`.
- Mailbox Agent discovers the WhatsApp Agent card at `http://127.0.0.1:9002` and sends a task payload:

```json
{
  "sender": "Ada <ada@x.com>",
  "subject": "Job opening",
  "priority": true,
  "snippet": "We have an opportunity for you."
}
```

Priority is **rule-based** (whole-word match on the configured keywords) so DeepSeek R1 1.5B cannot miss a flag. The model is used to clean sender/subject and to format the WhatsApp text.

## MCP tools

| Server | Tools |
|--------|--------|
| `email-mcp` | `ping`, `list_unread`, `fetch_message`, `mark_seen` |
| `whatsapp-mcp` | `send_notification` |

Agents spawn the servers as stdio subprocesses. You can also run them directly:

```bash
a2a-email-mcp
a2a-whatsapp-mcp
```

Processed IMAP `Message-ID`s are stored in `data/state/agent.db` so re-runs do not re-notify.

## Logging

- Console (human-readable)
- `logs/agents.log` (JSON lines)

Logged: agent start/stop, A2A inbound/outbound, MCP tool entry/exit, IMAP fetch counts, Ollama calls (DEBUG), WhatsApp send result. Passwords and tokens are redacted.

## Tests

```bash
pytest
```

## Project layout

```
src/a2a_mail_notify/
  runner.py                 CLI: run / status
  agents/                   A2A servers (mailbox + WhatsApp)
  mcp_servers/              email-mcp + whatsapp-mcp
  providers/                IMAP, Meta, Twilio
  llm/ollama.py             DeepSeek R1 1.5B client
  services/                 mailbox + WhatsApp business logic
```

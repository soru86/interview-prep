# Recruiter Agent — Architecture

Detailed flow and sequence diagrams mapped to actual source files and functions.

---

## 1. High-level system flow (`recruiter-agent run`)

```mermaid
flowchart TB
    subgraph CLI["main.py"]
        A["main()"] --> B["build_parser()"]
        B --> C["asyncio.run(async_main())"]
        C --> D["get_settings()<br/>config.py"]
        C --> E["configure_logging()<br/>utils/logging.py"]
        C --> F["Orchestrator.__init__()<br/>pipeline/orchestrator.py"]
        C --> G["Orchestrator.run()"]
    end

    subgraph Init["Orchestrator.__init__() wires"]
        F --> F1["OllamaClient()<br/>providers/llm/ollama.py"]
        F --> F2["GmailProvider()<br/>providers/email/gmail.py"]
        F --> F3["StateDB()<br/>storage/state_db.py"]
        F --> F4["ExcelTracker()<br/>storage/excel_tracker.py"]
        F --> F5["RecruiterFilter()<br/>pipeline/recruiter_filter.py"]
        F --> F6["JobExtractor()<br/>pipeline/job_extractor.py"]
        F --> F7["ResumeMatcher()<br/>pipeline/resume_matcher.py"]
        F --> F8["ReplyDrafter()<br/>pipeline/reply_drafter.py"]
        F --> F9["build_notifier()<br/>notifications/__init__.py"]
    end

    subgraph Run["Orchestrator.run()"]
        G --> H["initialize()"]
        H --> H1["StateDB.initialize()"]
        H --> I["load_resume_text()<br/>utils/resume_parser.py"]
        I --> J["GmailProvider.fetch_labeled_emails()"]
        J --> K{{"for each EmailMessage"}}
        K --> L["StateDB.is_processed()"]
        L -->|already done| K
        L -->|new| M["Orchestrator._process_email()"]
        M -->|exception| N["StateDB.mark_processed(ERROR)"]
        N --> K
        M -->|success| K
    end

    G --> O["return stats dict"]
    O --> P["print JSON to stdout"]
```

---

## 2. Per-email processing flow (`Orchestrator._process_email`)

```mermaid
flowchart TD
    START(["Orchestrator._process_email()"]) --> INC["stats['processed'] += 1"]

    INC --> FILTER{"RecruiterFilter.is_recruiter()<br/>pipeline/recruiter_filter.py"}

    FILTER -->|False| FIN_SKIP1["Orchestrator._finalize()<br/>status=SKIPPED, score=0"]

    FILTER -->|True| EXTRACT["JobExtractor.extract()<br/>pipeline/job_extractor.py"]
    EXTRACT --> MATCH["ResumeMatcher.match()<br/>pipeline/resume_matcher.py"]

    MATCH --> REC{{"match.recommendation"}}

    REC -->|SKIP| FIN_SKIP2["Orchestrator._finalize()<br/>status=SKIPPED"]
    REC -->|REVIEW| FIN_REVIEW["Orchestrator._finalize()<br/>status=REVIEW"]
    REC -->|APPLY| DRAFT["ReplyDrafter.create_draft()<br/>pipeline/reply_drafter.py"]

    DRAFT --> WA["Notifier.send_draft_notification()<br/>notifications/whatsapp.py"]
    WA --> FIN_DRAFT["Orchestrator._finalize()<br/>status=DRAFTED<br/>reply_date=StateDB.now()"]

    FIN_SKIP1 --> FINALIZE
    FIN_SKIP2 --> FINALIZE
    FIN_REVIEW --> FINALIZE
    FIN_DRAFT --> FINALIZE

    subgraph FINALIZE["Orchestrator._finalize()"]
        FINALIZE --> T1["ExcelTracker.upsert_row()<br/>storage/excel_tracker.py"]
        FINALIZE --> T2["StateDB.mark_processed()<br/>storage/state_db.py"]
    end

    FINALIZE --> END(["return"])
```

---

## 3. Recruiter filter detail

```mermaid
flowchart LR
    A["RecruiterFilter.is_recruiter()"] --> B{"RecruiterFilter.passes_heuristics()"}
    B -->|keywords/domains match| C["return True"]
    B -->|no match| D["OllamaClient.is_recruiter_email()<br/>providers/llm/ollama.py"]
    D --> E["OllamaClient._chat()"]
    E --> F["extract_json_object()<br/>utils/resume_parser.py"]
    F --> G["return is_recruiter bool"]
```

Heuristic keywords and domains are loaded from `config/settings.yaml` via `Settings.model_post_init()` in `config.py`.

---

## 4. LLM call chain (Ollama / DeepSeek R1)

```mermaid
flowchart TB
    subgraph JobExtractor
        JE1["JobExtractor.extract()"] --> JE2["OllamaClient.extract_job_details()"]
        JE2 --> JE3["OllamaClient._chat()"]
        JE3 --> JE4["extract_json_object()"]
        JE4 --> JE5["JobDetails.model_validate()"]
    end

    subgraph ResumeMatcher
        RM1["ResumeMatcher.match()"] --> RM2["OllamaClient.match_resume()"]
        RM2 --> RM3["OllamaClient._chat()"]
        RM3 --> RM4["extract_json_object()"]
        RM4 --> RM5["MatchResult.model_validate()"]
        RM5 --> RM6{"score >= threshold<br/>AND recommendation=SKIP?"}
        RM6 -->|yes| RM7["promote to REVIEW<br/>(in ResumeMatcher.match)"]
    end

    subgraph ReplyDrafter
        RD1["ReplyDrafter.create_draft()"] --> RD2["OllamaClient.draft_reply()"]
        RD2 --> RD3["OllamaClient._chat()"]
        RD3 --> RD4["extract_json_object()"]
        RD4 --> RD5["DraftReply.model_validate()"]
    end

    JE3 & RM3 & RD3 --> HTTP["POST {ollama_base_url}/api/chat<br/>(httpx.AsyncClient)"]
```

---

## 5. Gmail fetch & draft detail

```mermaid
flowchart TB
    subgraph Fetch["GmailProvider.fetch_labeled_emails()"]
        F1["_get_service()"] --> F2["_get_label_id()"]
        F2 --> F3["Gmail API: users().messages().list()"]
        F3 --> F4["Gmail API: users().messages().get(format=full)"]
        F4 --> F5["_parse_message()"]
        F5 --> F6["_parse_from_header()"]
        F5 --> F7["_extract_body()"]
        F5 --> F8["EmailMessage(...)"]
    end

    subgraph Draft["GmailProvider.create_draft() — if not DRY_RUN"]
        D1["_get_service()"] --> D2["_build_mime_message()"]
        D2 --> D3["attach MIMEText body"]
        D2 --> D4["attach MIMEApplication CV"]
        D2 --> D5["base64 encode raw MIME"]
        D5 --> D6["Gmail API: users().drafts().create()"]
    end
```

OAuth is handled in `_get_service()`: reads `token.json`, refreshes expired tokens, or runs `InstalledAppFlow.run_local_server()` using `credentials.json`.

---

## 6. WhatsApp notification detail (Meta default)

```mermaid
flowchart LR
    A["build_notifier()<br/>notifications/__init__.py"] --> B{"whatsapp_provider"}
    B -->|meta| C["MetaWhatsAppNotifier()"]
    B -->|twilio| D["TwilioWhatsAppNotifier()"]
    B -->|other| E["NullNotifier()"]

    C --> F["send_draft_notification()"]
    F --> G{"message_mode"}
    G -->|template| H["_build_template_payload()"]
    G -->|text| I["_build_text_payload()"]
    H & I --> J["_send()"]
    J --> K["POST graph.facebook.com/{version}/{phone_number_id}/messages"]
```

---

## 7. Sequence diagram — full `recruiter-agent run`

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant main as main.py<br/>main() / async_main()
    participant cfg as config.py<br/>get_settings()
    participant log as utils/logging.py<br/>configure_logging()
    participant orch as pipeline/orchestrator.py<br/>Orchestrator
    participant state as storage/state_db.py<br/>StateDB
    participant resume as utils/resume_parser.py<br/>load_resume_text()
    participant gmail as providers/email/gmail.py<br/>GmailProvider
    participant filt as pipeline/recruiter_filter.py<br/>RecruiterFilter
    participant ollama as providers/llm/ollama.py<br/>OllamaClient
    participant extract as pipeline/job_extractor.py<br/>JobExtractor
    participant match as pipeline/resume_matcher.py<br/>ResumeMatcher
    participant draft as pipeline/reply_drafter.py<br/>ReplyDrafter
    participant wa as notifications/whatsapp.py<br/>MetaWhatsAppNotifier
    participant excel as storage/excel_tracker.py<br/>ExcelTracker

    User->>main: recruiter-agent run
    main->>cfg: get_settings()
    main->>log: configure_logging(log_level)
    main->>orch: Orchestrator(settings)

    Note over orch: __init__() creates OllamaClient, GmailProvider,<br/>StateDB, ExcelTracker, RecruiterFilter,<br/>JobExtractor, ResumeMatcher, ReplyDrafter,<br/>build_notifier()

    main->>orch: run(max_emails)
    orch->>state: initialize()
    orch->>resume: load_resume_text(resume_folder)
    resume-->>orch: (resume_text, resume_path)

    orch->>gmail: fetch_labeled_emails(label, max_results)
    gmail->>gmail: _get_service()
    gmail->>gmail: _get_label_id()
    gmail->>gmail: messages().list() + messages().get()
    gmail->>gmail: _parse_message() per message
    gmail-->>orch: list[EmailMessage]

    loop each email
        orch->>state: is_processed(message_id)
        alt already processed
            state-->>orch: True → skip
        else new email
            state-->>orch: False
            orch->>orch: _process_email(email, resume_text, resume_path, stats)

            orch->>filt: is_recruiter(email)
            alt passes_heuristics() = True
                filt-->>orch: True
            else LLM classification
                filt->>ollama: is_recruiter_email(subject, body, sender)
                ollama->>ollama: _chat() → extract_json_object()
                ollama-->>filt: bool
                filt-->>orch: bool
            end

            alt not recruiter
                orch->>orch: _finalize(SKIPPED)
            else is recruiter
                orch->>extract: extract(email)
                extract->>ollama: extract_job_details(subject, body)
                ollama->>ollama: _chat() → extract_json_object()
                ollama-->>extract: JobDetails
                extract-->>orch: JobDetails

                orch->>match: match(job, resume_text)
                match->>ollama: match_resume(job, resume_text, threshold)
                ollama->>ollama: _chat() → extract_json_object()
                ollama-->>match: MatchResult
                match->>match: adjust SKIP→REVIEW if score≥threshold
                match-->>orch: MatchResult

                alt recommendation = SKIP
                    orch->>orch: _finalize(SKIPPED)
                else recommendation = REVIEW
                    orch->>orch: _finalize(REVIEW)
                else recommendation = APPLY
                    orch->>draft: create_draft(email, job, resume_text, resume_path)
                    draft->>ollama: draft_reply(...)
                    ollama->>ollama: _chat() → extract_json_object()
                    ollama-->>draft: DraftReply
                    alt DRY_RUN = false
                        draft->>gmail: create_draft(to, subject, body, thread_id, CV)
                        gmail->>gmail: _build_mime_message()
                        gmail->>gmail: drafts().create()
                    end
                    draft-->>orch: DraftReply

                    orch->>wa: send_draft_notification(...)
                    wa->>wa: _build_template_payload() or _build_text_payload()
                    wa->>wa: _send() → POST graph.facebook.com/.../messages
                    wa-->>orch: done

                    orch->>orch: _finalize(DRAFTED, reply_date=StateDB.now())
                end

                orch->>excel: upsert_row(TrackerRow)
                excel->>excel: _ensure_workbook()
                orch->>state: mark_processed(ProcessedEmailRecord)
            end
        end
    end

    orch-->>main: stats dict
    main-->>User: JSON printed to stdout
```

---

## 8. Sequence diagram — `recruiter-agent status`

```mermaid
sequenceDiagram
    actor User
    participant main as main.py<br/>async_main()
    participant orch as pipeline/orchestrator.py<br/>Orchestrator
    participant state as storage/state_db.py<br/>StateDB

    User->>main: recruiter-agent status
    main->>orch: Orchestrator(settings)
    main->>orch: status()
    orch->>orch: initialize()
    orch->>state: count_processed()
    state-->>orch: int
    orch->>orch: check resume_folder for files
    orch-->>main: {processed_emails, tracker_path,<br/>resume_configured, ollama_model, match_threshold}
    main-->>User: JSON printed
```

---

## 9. Match recommendation → action

```mermaid
flowchart LR
    A["ResumeMatcher.match()"] --> B{"recommendation"}
    B -->|SKIP| C["_finalize(SKIPPED)"]
    B -->|REVIEW| D["_finalize(REVIEW)<br/>no draft, no WhatsApp"]
    B -->|APPLY| E["ReplyDrafter.create_draft()"]
    E --> F["MetaWhatsAppNotifier.send_draft_notification()"]
    F --> G["_finalize(DRAFTED)"]

    C & D & G --> H["ExcelTracker.upsert_row()"]
    H --> I["StateDB.mark_processed()"]
```

`APPLY` is returned by `OllamaClient.match_resume()` when score ≥ `MATCH_THRESHOLD` (default 70). `ResumeMatcher.match()` additionally promotes `SKIP` → `REVIEW` when score ≥ threshold but the LLM said `SKIP`.

---

## 10. File → class → key functions reference

| Source file | Class / function | Role |
|-------------|------------------|------|
| `main.py` | `main()`, `async_main()`, `build_parser()` | CLI entry |
| `config.py` | `get_settings()`, `Settings` | Load `.env` + `config/settings.yaml` |
| `pipeline/orchestrator.py` | `Orchestrator.run()`, `_process_email()`, `_finalize()` | Main coordinator |
| `pipeline/recruiter_filter.py` | `RecruiterFilter.is_recruiter()`, `passes_heuristics()` | Filter recruiter emails |
| `pipeline/job_extractor.py` | `JobExtractor.extract()` | Extract job details |
| `pipeline/resume_matcher.py` | `ResumeMatcher.match()` | Score resume vs job |
| `pipeline/reply_drafter.py` | `ReplyDrafter.create_draft()` | LLM reply + Gmail draft |
| `providers/llm/ollama.py` | `OllamaClient._chat()`, `extract_job_details()`, `match_resume()`, `draft_reply()`, `is_recruiter_email()` | DeepSeek R1 via Ollama |
| `providers/email/gmail.py` | `GmailProvider.fetch_labeled_emails()`, `create_draft()` | Gmail read + draft |
| `utils/resume_parser.py` | `load_resume_text()`, `extract_json_object()` | Read CV + parse LLM JSON |
| `storage/state_db.py` | `StateDB.is_processed()`, `mark_processed()` | Idempotency (SQLite) |
| `storage/excel_tracker.py` | `ExcelTracker.upsert_row()` | Excel tracking |
| `notifications/__init__.py` | `build_notifier()` | Pick Meta / Twilio / Null |
| `notifications/whatsapp.py` | `MetaWhatsAppNotifier.send_draft_notification()` | WhatsApp alert |
| `models/domain.py` | `EmailMessage`, `JobDetails`, `MatchResult`, `DraftReply`, `TrackerRow` | Domain models |

---

## 11. External dependencies per run

| Service | Used by | Purpose |
|---------|---------|---------|
| Gmail API | `GmailProvider` | Fetch labeled emails, create drafts |
| Ollama (Docker) | `OllamaClient` | Job extraction, matching, reply drafting, recruiter classification |
| Meta Graph API | `MetaWhatsAppNotifier` | WhatsApp draft alerts |
| SQLite (`data/state/agent.db`) | `StateDB` | Processed email deduplication |
| Excel (`data/tracker/recruiter_tracker.xlsx`) | `ExcelTracker` | Recruiter interaction log |
| Resume file (`data/resume/`) | `load_resume_text()` | CV text + attachment |

---

## 12. Error handling path

```mermaid
flowchart TD
    A["Orchestrator.run() loop"] --> B["Orchestrator._process_email()"]
    B -->|uncaught Exception| C["log.exception()"]
    C --> D["stats['errors'] += 1"]
    D --> E["StateDB.mark_processed()<br/>status=ERROR, error_message"]
    E --> F["continue to next email"]
    B -->|success| F
```

Errors during individual email processing do not stop the batch. The email is marked `ERROR` in SQLite so it won't be retried unless the record is cleared manually.

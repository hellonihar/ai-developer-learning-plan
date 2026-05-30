# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Browser (localhost:5173)                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Contract │  │ Instructions │  │ Voice Note   │  │ Results   │  │
│  │ Upload   │  │ Input        │  │ Record/Upload│  │ Display   │  │
│  └────┬─────┘  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘  │
│       └───────────────┴─────────────────┴────────────────┘        │
│                              │ POST /api/contract/analyze          │
│                              │ multipart/form-data                 │
└──────────────────────────────┼─────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                    Vite Dev Proxy (port 5173 → 8000)               │
│                    vite.config.js → proxy: /api                    │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (localhost:8000)                │
│                                                                     │
│  ┌──────────────┐    ┌────────────────┐    ┌────────────────────┐  │
│  │  Router       │───▶│  Services      │───▶│  External APIs    │  │
│  │  contract.py  │    │                │    │                    │  │
│  │               │    │  pdf_processor │    │  Groq LLM          │  │
│  │  POST /analyze│    │  │             │    │  (json mode)       │  │
│  │  GET /health  │    │  voice_proc.   │    │                    │  │
│  └───────┬───────┘    │  (Whisper opt) │    └────────────────────┘  │
│          │            │                │                            │
│          │            │  contract_     │                            │
│          │            │  analyzer      │                            │
│          ▼            └────────────────┘                            │
│  ┌────────────────┐                                                 │
│  │  Models/Schemas│                                                 │
│  │  Pydantic      │                                                 │
│  └────────────────┘                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
intelligent_contract_review_assistant/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app factory, CORS, lifecycle
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── contract.py            # API endpoint definitions
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── pdf_processor.py       # PDF text extraction
│   │       ├── voice_processor.py     # Audio transcription (Whisper)
│   │       └── contract_analyzer.py   # LLM interaction and response parsing
│   ├── .env                           # Local config (gitignored)
│   ├── .env.example                   # Configuration template
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Root component, state, submit flow
│   │   ├── main.jsx                   # React entry point
│   │   ├── index.css                  # Tailwind directives
│   │   ├── services/
│   │   │   └── api.js                 # Axios HTTP client
│   │   └── components/
│   │       ├── ContractUpload.jsx     # PDF drag-and-drop uploader
│   │       ├── VoiceNoteInput.jsx     # Microphone recorder + file picker
│   │       ├── RiskSummary.jsx        # Score circle + summary text
│   │       ├── HighlightedClauses.jsx # Color-coded clause list
│   │       └── RecommendedRevisions.jsx # Before/after revision cards
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                 # Dev proxy, build config
│   ├── tailwind.config.js
│   └── postcss.config.js
├── samples/
│   ├── generate_samples.py            # Script to produce test PDFs
│   ├── contract_high_risk.pdf
│   ├── contract_moderate_risk.pdf
│   └── contract_low_risk.pdf
├── start.ps1                          # Launch both servers
├── README.md
└── ARCHITECTURE.md
```

## Backend Architecture

### Layers

The backend follows a three-layer design:

| Layer | Directory | Responsibility |
|---|---|---|
| **Router** | `routers/` | HTTP concerns: parse request, validate input, return response |
| **Service** | `services/` | Business logic: extract PDF, transcribe audio, call LLM |
| **Model** | `models/` | Data contracts: Pydantic schemas for serialization |

Dependencies flow inward: Router → Service → External APIs. Models are shared across all layers.

### Entry Point (`main.py`)

- Creates the `FastAPI` application with title, version, and OpenAPI metadata
- Configures CORS middleware from `CORS_ORIGINS` env var (comma-separated)
- Mounts the contract router at `/api/contract`
- Exposes `GET /api/health` for health checks
- Uses `python-dotenv` (loaded in `contract_analyzer.py`) to read `.env`

### Router (`routers/contract.py`)

A single endpoint `POST /api/contract/analyze` accepts multipart form data:

| Field | Type | Required | Source |
|---|---|---|---|
| `file` | `UploadFile` | Yes | PDF binary |
| `instructions` | `str` | No | Form field |
| `voice_note` | `UploadFile` | No | Audio binary |

The request lifecycle inside the router:

1. **Validate** — reject non-PDF files with 400
2. **Transcribe** — if voice_note present, pass to `voice_processor`, log warning on failure (non-fatal)
3. **Extract** — read PDF bytes, pass to `pdf_processor`, fail hard on extraction errors
4. **Analyze** — pass extracted text + instructions + transcription to `contract_analyzer`, return 500 on LLM failure
5. **Respond** — map results into `ContractAnalysisResponse` and return

### Service: PDF Processor (`services/pdf_processor.py`)

- Uses `pypdf.PdfReader` to parse PDF from a byte stream
- Iterates over all pages, prepending `--- Page N ---` markers
- Joins pages with double newlines
- Raises `ValueError` if no text can be extracted (e.g., scanned image PDF)
- Pure function: `bytes → str`

### Service: Voice Processor (`services/voice_processor.py`)

- Optional module — gracefully degrades if `openai-whisper` is not installed
- Uses try/except import at module level and sets `WHISPER_AVAILABLE` flag
- When whisper is available: loads the `"base"` model, transcribes from byte stream
- Returns a descriptive fallback string when whisper is absent

### Service: Contract Analyzer (`services/contract_analyzer.py`)

Core AI logic:

1. **Prompt construction** — builds a structured prompt with three optional sections:
   - `=== CONTRACT ===` — the full extracted text
   - `=== USER INSTRUCTIONS ===` — free-form review guidance
   - `=== VOICE NOTES FROM LEGAL TEAM ===` — transcribed audio

2. **LLM call** — sends to a configurable Groq model with:
   - `temperature=0.1` for deterministic, low-creativity output
   - `response_format={"type": "json_object"}` to enforce valid JSON
   - System prompt that defines the JSON schema and review focus areas

3. **Response parsing** — deserializes the JSON into:
   - `risk_summary` (str)
   - `risk_score` (int, 1-100)
   - `highlighted_clauses` (list of `ClauseHighlight`)
   - `recommended_revisions` (list of `RecommendedRevision`)

Configuration via environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | — | Groq authentication |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Model identifier |

### Models (`models/schemas.py`)

Pydantic v2 models for type validation and OpenAPI schema generation:

```
ContractAnalysisRequest       (request body — not currently used)
  ├── instructions: str
  └── voice_note_text: str

ClauseHighlight               (nested in response)
  ├── clause: str
  ├── risk_level: str         # "high" | "medium" | "low"
  └── explanation: str

RecommendedRevision           (nested in response)
  ├── clause: str
  ├── current_text: str
  ├── suggested_revision: str
  └── reason: str

ContractAnalysisResponse      (response body)
  ├── filename: str
  ├── risk_summary: str
  ├── risk_score: int
  ├── highlighted_clauses: list[ClauseHighlight]
  └── recommended_revisions: list[RecommendedRevision]

ErrorResponse                 (error body)
  └── detail: str
```

## Frontend Architecture

### Component Tree

```
<App>
  ├── <header>                         # Sticky nav bar
  ├── <form>                           # Main input area
  │   ├── <ContractUpload>             # Drop zone / file picker
  │   ├── <input>                      # Instructions text field
  │   ├── <VoiceNoteInput>             # Record button + audio upload
  │   └── <button>                     # Submit (disabled during load)
  ├── <div.error>                      # Conditional error banner
  └── [if result]
      ├── <RiskSummary>                # Score + text
      ├── <HighlightedClauses>         # Clause list
      └── <RecommendedRevisions>       # Revision cards
```

### State Management

All state lives in `App.jsx` via `useState` — no global state manager:

| State | Type | Purpose |
|---|---|---|
| `file` | `File | null` | Selected PDF |
| `instructions` | `string` | Review instructions text |
| `voiceNote` | `File | null` | Recorded/uploaded audio |
| `result` | `object | null` | `ContractAnalysisResponse` |
| `loading` | `boolean` | Submission in progress |
| `error` | `string` | Error message |

### Component Responsibilities

**ContractUpload** — Handles drag-and-drop and click-to-browse. Validates `application/pdf` on drop. Displays filename and size after selection. Hidden `<input type="file" accept=".pdf">`.

**VoiceNoteInput** — Two modes:
- *Record*: Uses `MediaRecorder` API with `audio/webm` MIME type. Hold-to-record UX (mousedown start, mouseup/leave stop). Creates a `File` from the recorded blob.
- *Upload*: Standard `<input type="file" accept="audio/*">`.
- Falls back to alert if microphone access denied.

**RiskSummary** — Displays the score in a colored circle (green < 40, yellow 40-69, red ≥ 70) alongside the summary text.

**HighlightedClauses** — Renders each clause as a card with left border color and badge matching risk level. Filters out empty clause lists.

**RecommendedRevisions** — For each revision, shows a "current" block (red) and "suggested" block (green) side by side, with the reason below.

### HTTP Client (`services/api.js`)

- Axios instance with `baseURL: '/api'` and 120-second timeout
- `analyzeContract()` builds a `FormData` with file, instructions, and optional audio
- During Vite dev, the `/api` prefix is proxied to `http://localhost:8000` (see `vite.config.js`)

## Data Flow — Request Lifecycle

```
User uploads PDF + instructions + voice note
        │
        ▼
FormData assembled in App.jsx
        │
        ▼
axios.post('/api/contract/analyze', formData)
        │
        ▼
Vite dev proxy → http://localhost:8000
        │
        ▼
FastAPI reads multipart fields
        │
        ├── voice_note present? ──Yes──▶ voice_processor.transcribe_audio()
        │                                    └── whisper (optional) → text
        │                                    └── on failure: log warning, continue
        │
        └── pdf file ───────────────────▶ pdf_processor.extract_text_from_pdf()
                                             └── pypdf → page-by-page text
                                             └── on failure: 400 error
        │
        ▼
contract_analyzer.analyze_contract(text, instructions, voice_text)
        │
        ├── Build prompt with === CONTRACT ===, === INSTRUCTIONS ===, === VOICE ===
        ├── POST to Groq with json_object response_format
        ├── Parse JSON → Pydantic models
        │
        ▼
ContractAnalysisResponse → JSON response
        │
        ▼
App.jsx setResult(data)
        │
        ▼
React renders <RiskSummary>, <HighlightedClauses>, <RecommendedRevisions>
```

## API Design

### `POST /api/contract/analyze`

**Request:** `multipart/form-data`

**Response `200 OK`:** `ContractAnalysisResponse`

```
{
  "filename": "contract.pdf",
  "risk_summary": "...",
  "risk_score": 72,
  "highlighted_clauses": [
    {
      "clause": "2. PAYMENT TERMS",
      "risk_level": "high",
      "explanation": "15-day payment window..."
    }
  ],
  "recommended_revisions": [
    {
      "clause": "4. LIABILITY",
      "current_text": "VENDOR'S TOTAL LIABILITY...",
      "suggested_revision": "Each party's liability...",
      "reason": "Mutual limitation is standard..."
    }
  ]
}
```

**Error responses:**
- `400` — Invalid file type, PDF read failure
- `500` — LLM analysis failure, internal error

### `GET /api/health`

**Response `200 OK`:** `{"status": "ok"}`

## Key Design Decisions

### 1. Service-layer LLM abstraction
The `contract_analyzer` service encapsulates all LLM interaction behind a single function. Swapping providers (Groq → OpenAI → Anthropic) requires changing only this file and its env vars.

### 2. Voice transcription as optional dependency
Whisper is a heavy dependency (several GB of model weights). It's imported lazily and the app works without it. The user gets a clear message that transcription is unavailable rather than a crash.

### 3. JSON mode for structured output
The LLM is constrained with `response_format: json_object` and a detailed system prompt defining the exact schema. This eliminates the need for fragile regex or string parsing on the response.

### 4. Proxy-only frontend integration
The frontend knows nothing about the backend address. All `/api` calls are proxied through Vite in development and would be served from the same origin in production (FastAPI can serve the built static files). No CORS issues after deploy.

### 5. Hold-to-record UX
The voice recorder uses `mousedown`/`mouseup` instead of toggle buttons. This is intentional — it mimics walkie-talkie behavior that feels natural for short voice notes and reduces the chance of accidentally sending empty recordings.

### 6. Stateless architecture
No database, no sessions, no file storage. PDFs and audio are held in memory only during the request. This keeps deployment simple (single `uvicorn` process) at the cost of no history or persistence between sessions.

## Error Handling Strategy

| Layer | Approach |
|---|---|
| Router | `HTTPException` with structured JSON `{ "detail": "..." }` |
| PDF Service | Raises `ValueError` on empty extraction; caught by router → 400 |
| Voice Service | Returns fallback string on any failure; never raises |
| LLM Service | Raises on empty response or JSON decode failure; caught by router → 500 |
| Frontend | Catches axios errors, extracts `response.data.detail` or `message`, displays in red banner |

## Configuration Reference

```
# Required
GROQ_API_KEY=gsk-...                # Groq API key

# Optional
GROQ_MODEL=openai/gpt-oss-120b      # LLM model identifier
CORS_ORIGINS=http://localhost:5173   # Comma-separated allowed origins
```

The `.env` file is loaded by `python-dotenv` in `contract_analyzer.py` and is consumed via `os.getenv()` throughout the backend.

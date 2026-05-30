# Intelligent Contract Review Assistant

AI-powered contract analysis tool that ingests PDF contracts, user instructions, and legal team voice notes to produce risk summaries, highlighted clauses, and recommended revisions.

## Prerequisites

- **Python 3.11+** — backend (FastAPI)
- **Node.js 18+** — frontend (React + Vite)
- **OpenAI API key** — LLM analysis (any OpenAI-compatible endpoint works)

## Quick Start

### 1. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Copy the environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` to set at minimum `OPENAI_API_KEY`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
CORS_ORIGINS=http://localhost:5173
```

| Variable | Default | Notes |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. Your OpenAI or compatible API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Change for proxies (e.g., `https://api.openai.com/v1`) |
| `OPENAI_MODEL` | `gpt-4o` | Any model with JSON mode support |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated list of allowed origins |

### 2. Frontend setup

```bash
cd frontend
npm install
```

### 3. Run the application

```powershell
.\start.ps1
```

Or start each server manually in separate terminals:

```bash
# Terminal 1 — backend (port 8000)
cd backend
uvicorn app.main:app --reload

# Terminal 2 — frontend (port 5173)
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

## Usage

1. **Upload a PDF contract** — drag-and-drop or click to browse
2. **Enter review instructions** — e.g., `"Find payment risks"` or `"Check termination terms"`
3. **(Optional) Record or upload a voice note** — hold to record via microphone, or upload an audio file
4. **Click "Analyze Contract"**

After analysis you'll see:

- **Risk Summary** — overall risk score (1–100) and a plain-language summary
- **Highlighted Clauses** — each flagged clause tagged as high/medium/low risk with an explanation
- **Recommended Revisions** — current text vs. suggested rewrite with rationale

### Voice transcription

Voice transcription requires [OpenAI Whisper](https://github.com/openai/whisper):

```bash
pip install openai-whisper
```

Without it, voice notes are still accepted but their text content is passed through as a fallback message.

## Testing with sample contracts

Sample contracts are provided in the `samples/` directory:

| File | Risk Profile | What to look for |
|---|---|---|
| `contract_high_risk.pdf` | High (75–90) | 15-day payment terms, auto-renewal trap, 80% termination fee, liability cap covering own negligence, IP grab clause, unfriendly governing law |
| `contract_moderate_risk.pdf` | Moderate (40–55) | Mutual liability cap, 30-day cure period, auto-renewal with short notice window, CPI-based fee increases |
| `contract_low_risk.pdf` | Low (10–25) | Balanced termination (30-day for cause or convenience), mutual liability exclusions, fair IP vesting, proper security obligations |

To regenerate them:

```bash
cd samples
pip install fpdf2
python generate_samples.py
```

## Architecture

```
┌──────────────┐     POST /api/contract/analyze     ┌──────────────────────┐
│   Frontend   │ ──────────────────────────────────► │       Backend        │
│  React/Vite  │                                     │   FastAPI (Python)   │
│   :5173      │ ◄────────────────────────────────── │     :8000            │
└──────────────┘     JSON response                   └──────────────────────┘
                                                              │
                                                   ┌──────────┼──────────┐
                                                   ▼          ▼          ▼
                                             pypdf     Whisper*    OpenAI
                                           (PDF text)  (audio→text) (LLM)
```

### Backend

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI app, CORS, health check |
| `app/routers/contract.py` | `POST /api/contract/analyze` endpoint |
| `app/services/pdf_processor.py` | Extract text from PDF via pypdf |
| `app/services/voice_processor.py` | Transcribe audio via Whisper (optional) |
| `app/services/contract_analyzer.py` | Send contract + instructions to LLM and parse response |
| `app/models/schemas.py` | Pydantic request/response models |

### Frontend

| File | Purpose |
|---|---|
| `src/App.jsx` | Main app state and submit flow |
| `src/components/ContractUpload.jsx` | PDF drag-and-drop upload area |
| `src/components/VoiceNoteInput.jsx` | Record-to-file or upload audio |
| `src/components/RiskSummary.jsx` | Risk score circle + summary text |
| `src/components/HighlightedClauses.jsx` | Color-coded clause list |
| `src/components/RecommendedRevisions.jsx` | Before/after diff cards |
| `src/services/api.js` | Axios client with file upload |

## API Reference

### `POST /api/contract/analyze`

Accepts a multipart form with:

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | PDF file | Yes | Contract document |
| `instructions` | string | No | Free-form review instructions |
| `voice_note` | audio file | No | Voice memo (webm, mp3, wav, etc.) |

Returns `200 OK` with:

```json
{
  "filename": "contract.pdf",
  "risk_summary": "The contract contains onerous payment terms...",
  "risk_score": 72,
  "highlighted_clauses": [
    {
      "clause": "2. PAYMENT TERMS",
      "risk_level": "high",
      "explanation": "15-day payment window with 5% monthly interest..."
    }
  ],
  "recommended_revisions": [
    {
      "clause": "4. LIABILITY AND INDEMNIFICATION",
      "current_text": "VENDOR'S TOTAL LIABILITY...",
      "suggested_revision": "Each party's total liability...",
      "reason": "Liability cap should not apply to gross negligence..."
    }
  ]
}
```

### `GET /api/health`

Returns `{"status": "ok"}`.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, pypdf, OpenAI SDK
- **Frontend:** React 18, Vite, Tailwind CSS, Axios
- **AI:** OpenAI GPT-4o (JSON mode); Whisper for voice (optional)

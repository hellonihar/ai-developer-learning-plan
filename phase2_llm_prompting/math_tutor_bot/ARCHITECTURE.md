# Architecture

## Overview

Math Tutor Bot is a full-stack chatbot that solves math problems using an LLM. It follows a **client-server (SPA + REST API)** architecture with a Python/FastAPI backend and a React frontend.

```
┌─────────────────────────────────────────────┐
│              BROWSER (localhost:5173)        │
│  ┌───────────────────────────────────────┐  │
│  │  index.html → main.jsx → App.jsx     │  │
│  │  ├── Header                          │  │
│  │  ├── Sidebar (ExampleCards × 4)      │  │
│  │  ├── ChatArea (ChatMessage[])        │  │
│  │  └── InputBar                        │  │
│  └───────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │ POST /chat, GET /examples
                   ▼
┌─────────────────────────────────────────────┐
│            BACKEND (localhost:8000)          │
│  FastAPI App                                │
│  ├── GET  /health                           │
│  ├── GET  /examples                         │
│  └── POST /chat  →  LangChain → Groq API   │
│  prompts.py  (system prompt + few-shots)    │
│  .env        (GROQ_API_KEY)                 │
└──────────────────┬──────────────────────────┘
                   │ LLM inference
                   ▼
┌─────────────────────────────────────────────┐
│       GROQ CLOUD (llama-3.3-70b-versatile)  │
└─────────────────────────────────────────────┘
```

## Directory Layout

```
math_tutor_bot/
├── ARCHITECTURE.md
├── README.md
├── backend/
│   ├── .env                Groq API key
│   ├── main.py             FastAPI server, routes, LLM orchestration
│   ├── prompts.py          System prompt and few-shot examples
│   └── requirements.txt    Python dependencies
└── frontend/
    ├── index.html          HTML shell (loads KaTeX CSS from CDN)
    ├── package.json        npm config and dependencies
    ├── vite.config.js      Vite build config
    └── src/
        ├── main.jsx        React entry point
        ├── App.jsx         Root component (all UI logic)
        └── index.css       All styles (314 lines)
```

## Backend

**Stack:** Python, FastAPI, LangChain, LangChain-Groq, Pydantic

The backend is a single FastAPI application in `backend/main.py` with three endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check, returns `{"status": "ok"}` |
| `/examples` | GET | Returns the 4 few-shot examples for the sidebar |
| `/chat` | POST | Accepts message history, returns LLM-generated reply |

### POST /chat Flow

1. Request body is validated with a Pydantic `ChatRequest` model (list of `{role, content}` messages)
2. Messages are converted to LangChain format:
   - `SystemMessage(SYSTEM_PROMPT)` is prepended
   - `"user"` → `HumanMessage`, `"assistant"` → `AIMessage`
3. `ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3, max_tokens=2048).invoke()` is called
4. The response content is returned as `{"reply": "..."}`

### Prompts (`backend/prompts.py`)

- **`SYSTEM_PROMPT`** (82 lines): Defines the bot persona and Chain-of-Thought instructions. Mandates numbered steps, LaTeX notation, and a clear "Final Answer" section. Contains 4 embedded few-shot examples covering linear algebra, probability, geometry, and quadratic equations.
- **`FEW_SHOT_EXAMPLES`** (list of 4 dicts): Structured versions of the same examples, served via `GET /examples` for the frontend sidebar.

### Configuration

- **Groq API key** is loaded from `backend/.env` via `python-dotenv`
- **LLM parameters** (model, temperature, max_tokens) are hardcoded in `main.py`
- **CORS** allows `localhost:5173` and `127.0.0.1:5173`

## Frontend

**Stack:** React 18, Vite 6, react-markdown, remark-math, rehype-katex

The frontend is a single-page React app with no client-side routing.

### Components (all in `frontend/src/App.jsx`)

| Component | Responsibility |
|-----------|----------------|
| **App** (root) | Manages all state (messages, input, loading, examples, sidebar). Renders layout: header, sidebar, chat area, input bar. |
| **ChatMessage** | Renders a single message bubble. User messages render as plain `<p>`. Assistant messages render through `ReactMarkdown` with `remark-math` and `rehype-katex` for LaTeX. |
| **ExampleCard** | Clickable card in the sidebar showing a few-shot problem. Clicking populates the input field. |

### Data Flow

1. User types a problem and clicks Send
2. Frontend adds the user message to local state and POSTs the full conversation history to `/chat`
3. On success, the assistant's reply is appended to the message list and rendered with KaTeX
4. On mount, `GET /examples` fetches the 4 example problems for the sidebar

### Dependencies

| Package | Purpose |
|---------|---------|
| react-markdown | Renders Markdown in chat bubbles |
| remark-math | Parses LaTeX math in Markdown |
| rehype-katex | Renders LaTeX as styled math via KaTeX |
| KaTeX CSS (CDN) | Styles for rendered math expressions |

## Prompt Strategy

The system prompt in `prompts.py` uses **Chain-of-Thought prompting with few-shot examples**:

- The persona is set as a patient, encouraging math tutor
- The model is instructed to **always show step-by-step reasoning** before the final answer
- Each step must be numbered, use LaTeX notation, and explain the operation being performed
- **4 few-shot examples** are embedded directly in the system prompt, covering algebra, probability, and geometry
- Temperature is set to **0.3** for deterministic, reliable output

## Key Design Decisions

- **No database** — all state is ephemeral. Conversation history is sent with each request.
- **No tests** — the project has zero automated tests.
- **CoT in the prompt, not the code** — the backend does no math; it delegates all reasoning to the LLM.
- **Single-component frontend** — the entire UI lives in `App.jsx` without a router or state management library.

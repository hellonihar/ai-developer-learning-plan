# Policy Analyzer — Architecture

## Overview

A Streamlit-based RAG (Retrieval-Augmented Generation) application that analyzes insurance policy PDFs. Users upload a policy document, ask natural-language questions about its clauses, and receive structured chain-of-thought responses with plain-language explanations, risk assessments, and actionable implications.

The entire pipeline runs locally — no cloud API dependencies. The LLM is served via [LM Studio](https://lmstudio.ai/) on `localhost:1234/v1`, and embeddings use the local `all-MiniLM-L6-v2` sentence-transformer model.

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                           User (Browser)                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Streamlit Frontend (app.py)                   │  │
│  │                                                                  │  │
│  │  ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐  │  │
│  │  │ Upload Panel │    │ Model Config │    │  Query Interface  │  │  │
│  │  │ (PDF upload) │    │ (LM Studio   │    │  (text input +    │  │  │
│  │  │              │    │  model name) │    │   analysis view)  │  │  │
│  │  └──────┬───────┘    └──────────────┘    └─────────┬─────────┘  │  │
│  └─────────┼──────────────────────────────────────────┼─────────────┘  │
└────────────┼──────────────────────────────────────────┼────────────────┘
             │                                          │
             ▼                                          ▼
┌──────────────────────┐          ┌──────────────────────────────┐
│   PDF Ingestion      │          │     Query Pipeline           │
│                      │          │                              │
│  ┌────────────────┐  │          │  ┌────────────────────────┐  │
│  │ PyMuPDF (fitz) │  │          │  │ ChromaDB               │  │
│  │ extract_text() │  │          │  │ query(question, k=5)   │  │
│  └───────┬────────┘  │          │  └───────────┬────────────┘  │
│          ▼           │          │              │                │
│  ┌────────────────┐  │          │              ▼                │
│  │ LangChain      │  │          │  ┌────────────────────────┐  │
│  │ RecursiveChar  │  │          │  │ format_docs()          │  │
│  │ TextSplitter   │  │          │  │ format_examples()      │  │
│  │ chunk_size=1500│  │          │  └───────────┬────────────┘  │
│  │ overlap=200    │  │          │              │                │
│  └───────┬────────┘  │          │              ▼                │
│          ▼           │          │  ┌────────────────────────┐  │
│  ┌────────────────┐  │          │  │ CoT Prompt Builder     │  │
│  │ EmbeddingStore │  │          │  │ (system + few-shot +   │  │
│  │ add_chunks()   │  │          │  │  retrieved chunks)     │  │
│  │ (ChromaDB +    │  │          │  └───────────┬────────────┘  │
│  │  all-MiniLM)   │  │          │              │                │
│  └────────────────┘  │          │              ▼                │
│                      │          │  ┌────────────────────────┐  │
│  all-MiniLM-L6-v2    │          │  │ LM Studio              │  │
│  → 384-dim vectors   │          │  │ localhost:1234/v1      │  │
│                      │          │  │ Llama/Mistral/Phi etc  │  │
└──────────────────────┘          │  │ (user's choice)        │  │
                                   │  └────────────────────────┘  │
                                   │                              │
                                   │         Result: structured   │
                                   │         CoT analysis → UI     │
                                   └──────────────────────────────┘
```

---

## Component Breakdown

### 1. Frontend — `app.py`

| Section | Function |
|---------|----------|
| **Upload Panel** | Streamlit file uploader accepts `.pdf`. On upload, writes to a temp file → triggers ingestion pipeline. |
| **Model Config** | Text input for the LM Studio model name (e.g. `llama-3.2-3b-instruct`, `phi-4`, `mistral-7b`). Rebuilds the LangChain when changed. |
| **Query Interface** | Text input for user's question → retrieves top-5 relevant chunks from ChromaDB → invokes the LangChain → renders the LLM response. An expander shows the raw retrieved chunks for transparency. |

**State management** uses `st.session_state` to persist four values:
- `store` — `EmbeddingStore` instance (survives re-renders)
- `chain` — The LangChain `Runnable` (rebuilt on model change)
- `processed` — Flag to track whether a PDF has been indexed
- `model` — Current model name string

### 2. PDF Parser — `pipeline/pdf_parser.py`

Wraps PyMuPDF (`fitz`) to extract all text from every page, joining pages with double newlines. A single function:

```python
extract_text(pdf_path: str) -> str
```

### 3. Chunker — `pipeline/chunker.py`

Uses LangChain's `RecursiveCharacterTextSplitter` with:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `chunk_size` | 1500 | Balances context window usage with semantic coherence |
| `chunk_overlap` | 200 | Prevents clause boundaries from being lost at seams |
| `separators` | `["\n\n", "\n", ". ", " ", ""]` | Prefers paragraph/line/sentence boundaries before word-splitting |

Policy documents tend to have dense, clause-structured text. Starting with double-newline separators ensures most clauses stay intact.

### 4. Embeddings + Vector Store — `pipeline/embeddings.py`

The `EmbeddingStore` class encapsulates:

| Component | Detail |
|-----------|--------|
| **Embedding model** | `sentence-transformers/all-MiniLM-L6-v2` — 384-dim, fast, local, ~50MB on disk |
| **Vector DB** | ChromaDB with local persistent storage (`./chroma_db/`) |
| **Collection** | Named `policy_chunks`, auto-created on first use |
| **Search** | `query(text, k=5)` — cosine similarity, returns raw document strings |

Key methods:
- `add_chunks(chunks)` — generates UUIDs, embeds, stores
- `search(query, k=5)` — retrieves top-k chunks
- `reset()` — drops and recreates the collection (used on new uploads)

ChromaDB is chosen for zero-config operation — no external server, data persists to disk, and it is trivially swappable for Pinecone/Qdrant later.

### 5. RAG Chain — `pipeline/rag_chain.py`

The core LangChain LCEL (LangChain Expression Language) pipeline:

```python
chain = (
    RunnablePassthrough.assign(
        examples=RunnableLambda(lambda _: format_examples()),
        context=RunnableLambda(lambda x: format_docs(x["context"])),
    )
    | prompt
    | llm
)
```

**Steps in order:**

1. **`RunnablePassthrough.assign`** — Injects two computed fields without modifying the input:
   - `examples` → formatted few-shot strings (static per session)
   - `context` → retrieved chunks joined with `\n\n---\n\n` separators
2. **`ChatPromptTemplate`** — Renders the system + human prompt (see "CoT Prompting" below)
3. **`ChatOpenAI`** — Calls LM Studio's OpenAI-compatible endpoint at `http://localhost:1234/v1`

The `ChatOpenAI` class from `langchain-openai` is configured to point at the local LM Studio server, which accepts any `api_key` value. The `model` name must match whatever is loaded in LM Studio.

### 6. Few-Shot Examples — `few_shot_examples.py`

Three annotated examples covering:

| Example | Risk Level | What it demonstrates |
|---------|-----------|----------------------|
| Cyber exclusion clause | HIGH | Broad "directly or indirectly" language, trap wording, carve-back strategy |
| Records & cooperation | LOW | Standard boilerplate, favorable qualifiers, routine obligations |
| Arbitration clause | MEDIUM | Venue risk, cost-shifting analysis, negotiation leverage |

Each example contains four fields (`clause`, `explanation`, `risk_assessment`, `implication`) that mirror the exact structure the LLM is asked to produce. The `format_examples()` function serializes them into the system prompt.

### 7. Example PDF Generator — `examples/generate_pdfs.py`

Utility that converts `.txt` source files into `.pdf` using PyMuPDF's `insert_text()` with automatic page-breaking. Three sample policies:

| Policy | Topics covered |
|--------|----------------|
| `policy_01` — CGL Insurance | Coverage agreements, exclusions (cyber, pollution, employment, recall), arbitration, cooperation conditions |
| `policy_02` — Data Protection | GDPR/CCPA/PIPEDA compliance, data classification tiers, breach procedures, third-party processors, retention schedules |
| `policy_03` — Code of Conduct | Conflicts of interest, insider trading, anti-bribery, whistleblower protections, non-compete, social media policy |

---

## CoT Prompting Strategy

### Prompt Structure

```
SYSTEM: You are a senior policy compliance analyst...
        {examples}     <- 3 few-shot examples
        Follow this chain-of-thought for EACH clause:
          1. Explanation
          2. Risk Assessment
          3. Implication
        After analyzing: Overall Assessment + Recommended Actions

HUMAN:  Retrieved policy excerpts:
        {context}       <- top-5 ChromaDB chunks, joined by ---
        
        User question: {question}
        
        Analyze the relevant clauses...
```

### Design rationale

| Decision | Why |
|----------|-----|
| **Examples in system prompt, not human prompt** | Keeps them in context for the entire conversation, acts as a persistent formatting guide |
| **Per-clause CoT then synthesis** | Forces the LLM to analyze each clause independently before drawing cross-cutting conclusions, reducing hallucinations |
| **Risk classification (LOW/MEDIUM/HIGH)** | Provides a structured, scannable output that is useful for compliance dashboards |
| **"Implication" field** | Translates legalese into practical business impact — the most valuable output for non-lawyer users |
| **Recommended Actions** | Pushes the LLM from analysis to prescription, increasing actionable value |

The three few-shot examples were selected to cover—low, medium, and high-risk clauses—so the LLM sees the full spectrum of response shapes before generating its own.

---

## Key Design Decisions

| Decision | Choice | Alternative considered |
|----------|--------|----------------------|
| **LLM serving** | LM Studio (local, OpenAI-compatible) | Groq API, OpenAI API — rejected for local-first requirement |
| **Embedding model** | `all-MiniLM-L6-v2` (local, 384-dim) | `text-embedding-3-large` (OpenAI API, 3072-dim) — rejected to avoid API dependency |
| **Vector store** | ChromaDB (persistent, in-process) | Pinecone, Qdrant — rejected for zero-ops simplicity |
| **Orchestration** | LangChain LCEL | Raw HTTP calls — LCEL gives composable chains with minimal glue code |
| **UI framework** | Streamlit | React + FastAPI — Streamlit reaches MVP in ~100 lines |
| **PDF parsing** | PyMuPDF (`fitz`) | PyPDF2, pdfplumber — PyMuPDF is fastest and handles tables/layouts best |
| **Chunking** | RecursiveCharacterTextSplitter | Semantic chunking (expensive), fixed-size (loses structure) — recursive is the pragmatic middle |

---

## Running the Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate example PDFs (optional)
python examples/generate_pdfs.py

# 3. Start LM Studio, load a model, start the API server (default port 1234)

# 4. Launch the app
streamlit run app.py
```

Then open `http://localhost:8501` in a browser.

---

## File Reference

```
policy_analyzer/
├── app.py                          # Streamlit entry point
├── few_shot_examples.py            # 3 CoT few-shot examples
├── requirements.txt                # Python dependencies
├── .env.example                    # LM Studio config instructions
├── pipeline/
│   ├── __init__.py
│   ├── pdf_parser.py               # PyMuPDF text extraction
│   ├── chunker.py                  # RecursiveCharacterTextSplitter
│   ├── embeddings.py               # EmbeddingStore (ChromaDB + sentence-transformers)
│   └── rag_chain.py                # LangChain LCEL chain → LM Studio
└── examples/
    ├── generate_pdfs.py            # Converts .txt → .pdf
    ├── policy_01_commercial_liability.txt/.pdf
    ├── policy_02_data_protection.txt/.pdf
    └── policy_03_code_of_conduct.txt/.pdf
```

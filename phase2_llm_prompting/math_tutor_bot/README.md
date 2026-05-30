# Math Tutor Bot

An interactive chatbot that solves math problems step-by-step using Chain-of-Thought (CoT) reasoning and few-shot prompting. Built with FastAPI + LangChain + Groq on the backend and React + Vite on the frontend.

## Features

- **Step-by-step reasoning** — every response shows complete working before the final answer
- **4 few-shot examples** — algebra, probability, and geometry problems demonstrate the expected format
- **LaTeX math rendering** — proper mathematical notation using KaTeX
- **Example sidebar** — click any example to load it as a query

## Prerequisites

- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` with:
```
GROQ_API_KEY=gsk_your_key_here
```

Start the server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## Usage

1. Type a math problem in the input field (e.g., "Solve 3x + 7 = 22")
2. The bot responds with numbered step-by-step reasoning and a final answer
3. Click any example in the sidebar to load it as a query
4. Click "New Problem" to clear the conversation and start fresh

## Prompt Strategy

The system prompt enforces Chain-of-Thought reasoning with explicit instructions:
- Show complete step-by-step reasoning before the final answer
- Number each step and explain the operation being performed
- Use LaTeX notation for mathematical expressions
- Be encouraging and patient — the bot is a tutor

Four few-shot demonstrations (linear algebra, probability, geometry, quadratic algebra) are included in the prompt and also served via the `/examples` API endpoint for frontend display.

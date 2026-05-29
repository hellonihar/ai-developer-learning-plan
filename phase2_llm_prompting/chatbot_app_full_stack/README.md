# LangChain + Groq Chatbot

Full-stack chatbot with a FastAPI/LangChain/Groq backend and a React/Vite frontend.

## Project Structure

```
chatbot_app_full_stack/
├── backend/
│   ├── main.py              # FastAPI server, /chat endpoint, LangChain + Groq integration
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # GROQ_API_KEY environment variable
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Chat UI component (message list, input bar, API calls)
│   │   └── index.css        # Styles (bubbles, typing indicator, layout)
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Prerequisites

- **Python 3.11+** and pip
- **Node.js 18+** and npm
- A **Groq API key** from https://console.groq.com

## Setup & Run

### 1. Backend

```bash
cd backend
python -m pip install -r requirements.txt
```

Set your Groq API key in `backend/.env`:

```
GROQ_API_KEY=gsk_your_key_here
```

Start the server:

```bash
python -m uvicorn main:app --reload --port 8000
```

The API runs at `http://localhost:8000`. Test with `curl http://localhost:8000/health`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`.

### 3. Chat

Open the frontend URL in a browser and start sending messages.

## API

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/health` | GET | — | `{"status": "ok"}` |
| `/chat` | POST | `{"messages": [{"role": "user", "content": "..."}]}` | `{"reply": "..."}` |

The chat endpoint accepts a conversation history array and returns the assistant's reply using `llama-3.3-70b-versatile` via LangChain + Groq.

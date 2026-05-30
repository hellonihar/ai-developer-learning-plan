import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

load_dotenv()

app = FastAPI(title="Math Tutor Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key or groq_api_key == "your_groq_api_key_here":
    raise RuntimeError("GROQ_API_KEY is not configured. Set it in backend/.env")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=2048,
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/examples")
def get_examples():
    return {"examples": FEW_SHOT_EXAMPLES}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]

        for msg in req.messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            else:
                langchain_messages.append(AIMessage(content=msg.content))

        response = llm.invoke(langchain_messages)
        return ChatResponse(reply=response.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

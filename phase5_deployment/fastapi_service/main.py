import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="AI Service")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Query(BaseModel):
    prompt: str

class Response(BaseModel):
    result: str

@app.post("/generate", response_model=Response)
async def generate(query: Query):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query.prompt}],
        )
        return Response(result=resp.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

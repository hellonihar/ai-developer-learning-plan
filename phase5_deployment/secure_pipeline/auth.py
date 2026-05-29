import os
from functools import wraps
from fastapi import FastAPI, Depends, HTTPException, Header

app = FastAPI(title="Secure Pipeline")

API_KEY = os.getenv("API_KEY", "changeme")

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.get("/admin/data")
async def admin_data(auth=Depends(verify_key)):
    return {"secret": "This is sensitive data"}

@app.get("/public/info")
async def public_info():
    return {"info": "This is public"}

import io
import os
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

app = FastAPI(title="Multimodal Captioner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = 0 if os.environ.get("USE_CUDA", "0") == "1" else -1
torch_device = "cuda" if device >= 0 else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(torch_device)

MAX_FILE_SIZE = 10 * 1024 * 1024


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/caption")
def caption_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files are allowed")

    data = file.file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")

    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image file")

    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(torch_device) for k, v in inputs.items()}

    generated_ids = model.generate(**inputs, max_new_tokens=50)
    captions = [processor.decode(g, skip_special_tokens=True) for g in generated_ids]

    return {
        "captions": captions,
        "alt_text": captions[0] if captions else "",
    }

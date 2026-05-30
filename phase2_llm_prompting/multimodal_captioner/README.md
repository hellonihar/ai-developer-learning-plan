# Multimodal Captioner

Upload an image and get descriptive captions + alt-text using Hugging Face vision-language models (BLIP).

## Project Structure

```
multimodal_captioner/
├── backend/
│   ├── main.py              # FastAPI server, /caption endpoint, BLIP pipeline
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Upload UI + results display
│   │   └── index.css        # Dark theme styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup & Run

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

The model (`Salesforce/blip-image-captioning-base`) downloads on first run.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, upload an image, and click **Generate Caption**.

## API

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/health` | GET | — | `{"status": "ok"}` |
| `/caption` | POST | `multipart/form-data` with `file` field | `{"captions": [...], "alt_text": "..."}` |

## Model

Uses [BLIP (Salesforce/blip-image-captioning-base)](https://huggingface.co/Salesforce/blip-image-captioning-base) — a lightweight vision-language model fine-tuned for image captioning.

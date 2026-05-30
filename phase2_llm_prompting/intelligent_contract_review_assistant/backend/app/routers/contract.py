import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..models.schemas import (
    ContractAnalysisResponse,
    ClauseHighlight,
    RecommendedRevision,
)
from ..services.pdf_processor import extract_text_from_pdf
from ..services.voice_processor import transcribe_audio
from ..services.contract_analyzer import analyze_contract

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contract", tags=["contract"])


@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract_endpoint(
    file: UploadFile = File(...),
    instructions: str = Form(""),
    voice_note: UploadFile | None = File(None),
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="PDF file is required.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    voice_text = ""
    if voice_note:
        try:
            audio_bytes = await voice_note.read()
            if audio_bytes:
                voice_text = transcribe_audio(audio_bytes)
        except Exception as e:
            logger.warning(f"Voice transcription failed, continuing without it: {e}")

    try:
        pdf_bytes = await file.read()
        contract_text = extract_text_from_pdf(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

    try:
        risk_summary, risk_score, clauses, revisions = analyze_contract(
            contract_text=contract_text,
            instructions=instructions,
            voice_note=voice_text,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Contract analysis failed: {e}")

    return ContractAnalysisResponse(
        filename=file.filename or "contract.pdf",
        risk_summary=risk_summary,
        risk_score=risk_score,
        highlighted_clauses=clauses,
        recommended_revisions=revisions,
    )

import json
import logging
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
from ..models.schemas import ClauseHighlight, RecommendedRevision

logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_CONTRACT_CHARS = int(os.getenv("MAX_CONTRACT_CHARS", "18000"))

SYSTEM_PROMPT = """You are an expert contract review assistant. Analyze the given contract and return a JSON response with exactly these keys:
- risk_summary: A concise 2-3 sentence summary of the key risks found (string)
- risk_score: An integer from 1-100 indicating overall risk level (1=minimal risk, 100=extreme risk)
- highlighted_clauses: An array of objects, each with:
  - clause: The exact clause text or title (string)
  - risk_level: One of "high", "medium", "low" (string)
  - explanation: Why this clause is risky (string)
- recommended_revisions: An array of objects, each with:
  - clause: The clause title or identifier (string)
  - current_text: The problematic text (string)
  - suggested_revision: The proposed rewrite (string)
  - reason: Why this change is needed (string)

Focus on: payment terms, liability caps, indemnification, termination rights, confidentiality, IP ownership, governing law, force majeure, auto-renewal clauses, and any ambiguous language.

Return ONLY valid JSON. No markdown fences, no extra text."""


def _build_user_prompt(contract_text: str, instructions: str, voice_note: str) -> str:
    parts = [f"=== CONTRACT ===\n{contract_text}"]
    if instructions:
        parts.append(f"=== USER INSTRUCTIONS ===\n{instructions}")
    if voice_note:
        parts.append(f"=== VOICE NOTES FROM LEGAL TEAM ===\n{voice_note}")
    return "\n\n".join(parts)


def analyze_contract(
    contract_text: str,
    instructions: str = "",
    voice_note: str = "",
) -> tuple[str, int, list[ClauseHighlight], list[RecommendedRevision]]:
    logger.info("Starting contract analysis...")

    if len(contract_text) > MAX_CONTRACT_CHARS:
        logger.warning(
            "Contract text too long (%d chars); truncating to %d chars to fit model limits.",
            len(contract_text),
            MAX_CONTRACT_CHARS,
        )
        contract_text = (
            contract_text[:MAX_CONTRACT_CHARS]
            + "\n\n[...contract truncated due to size limit... ]"
        )

    user_prompt = _build_user_prompt(contract_text, instructions, voice_note)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from LLM")

    data = json.loads(content)

    risk_summary = data.get("risk_summary", "No summary provided.")
    risk_score = data.get("risk_score", 50)

    clauses = [ClauseHighlight(**c) for c in data.get("highlighted_clauses", [])]
    revisions = [
        RecommendedRevision(**r) for r in data.get("recommended_revisions", [])
    ]

    logger.info(
        f"Analysis complete: score={risk_score}, "
        f"clauses={len(clauses)}, revisions={len(revisions)}"
    )
    return risk_summary, risk_score, clauses, revisions

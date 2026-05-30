import logging

logger = logging.getLogger(__name__)

try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("whisper not installed. Voice transcription disabled.")


def transcribe_audio(audio_bytes: bytes) -> str:
    if not WHISPER_AVAILABLE:
        msg = (
            "Voice transcription is not available. "
            "Install openai-whisper to enable this feature."
        )
        logger.warning(msg)
        return f"[{msg}]"

    try:
        import io
        model = whisper.load_model("base")
        result = model.transcribe(io.BytesIO(audio_bytes))
        text = result["text"].strip()
        logger.info(f"Transcribed audio: {len(text)} chars")
        return text
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        return f"[Transcription error: {e}]"

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.audio import SpeechRequest
from app.services.audio_service import (
    AudioServiceError,
    EmptyTranscriptError,
    generate_speech,
    transcribe_audio,
)

router = APIRouter(
    prefix="/audio",
    tags=["audio"],
)

# Formats the browser MediaRecorder can produce
_ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/webm;codecs=opus",
    "audio/ogg",
    "audio/mp4",
    "audio/mpeg",
    "audio/wav",
}

_MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB


# ── STT ────────────────────────────────────────────────────────────────────

@router.post("/transcribe")
async def transcribe_endpoint(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if audio.content_type not in _ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported audio format: {audio.content_type}. "
                   "Allowed formats: webm, ogg, mp4, mpeg, wav.",
        )

    contents = await audio.read()

    if not contents:
        raise HTTPException(status_code=422, detail="Audio file is empty.")

    if len(contents) > _MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"Audio file too large. Maximum size is {_MAX_AUDIO_BYTES // (1024 * 1024)} MB.",
        )

    try:
        text = await transcribe_audio(contents, audio.content_type or "audio/webm")
    except EmptyTranscriptError:
        raise HTTPException(
            status_code=422,
            detail="Could not detect any speech in the audio. Please try again or type your answer.",
        )
    except AudioServiceError:
        # The real provider error is logged by the service — the client only
        # gets a safe, actionable message.
        raise HTTPException(
            status_code=502,
            detail="Voice transcription is temporarily unavailable. You can type your answer instead.",
        )

    return {"text": text}


# ── TTS ────────────────────────────────────────────────────────────────────

@router.post("/speech")
async def speech_endpoint(
    request: SpeechRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        audio_bytes = await generate_speech(request.text)
    except AudioServiceError:
        # The real provider error is logged by the service — the client only
        # gets a safe, actionable message.
        raise HTTPException(
            status_code=502,
            detail="Voice playback is temporarily unavailable. You can read the question and continue.",
        )

    return Response(content=audio_bytes, media_type="audio/mpeg")

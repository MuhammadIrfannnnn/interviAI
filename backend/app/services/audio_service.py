import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("interviai.audio")


class AudioServiceError(Exception):
    """Raised when an external audio provider call fails."""


class EmptyTranscriptError(AudioServiceError):
    """The provider accepted the audio but returned no usable transcript."""


class MissingAudioCredentialsError(AudioServiceError):
    """The audio provider credentials are not configured at all."""


# Connect fast, allow enough read time for provider latency — never freeze the
# request for minutes.
_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)

# Browser MIME types → file extension the provider expects.
_EXT_MAP = {
    "audio/webm": "webm",
    "audio/webm;codecs=opus": "webm",
    "audio/ogg": "ogg",
    "audio/mp4": "mp4",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
}


# ── Safe logging helpers ───────────────────────────────────────────────────

def _classify_status(status_code: int) -> str:
    """Bucket a non-2xx provider status into a failure category."""
    if status_code in (401, 403):
        return "auth_failure"
    if status_code == 402:
        # e.g. ElevenLabs free plan cannot use library voices via the API.
        return "plan_limitation"
    if 400 <= status_code < 500:
        return "invalid_request"
    return "provider_error"


def _log_provider_error(provider: str, operation: str, response: httpx.Response, **context: object) -> None:
    """Log a provider failure with safe context.

    Logs the failure category, HTTP status, the provider's error body
    (truncated) and non-secret context such as model/voice/audio metadata.
    NEVER logs API keys, partial API keys or Authorization headers.
    """
    body = response.text[:500].replace("\n", " ")
    extras = " ".join(f"{key}={value}" for key, value in context.items())
    logger.warning(
        "[audio] provider=%s operation=%s failure=%s status=%s %s body=%r",
        provider,
        operation,
        _classify_status(response.status_code),
        response.status_code,
        extras,
        body,
    )


def _log_transport_error(provider: str, operation: str, exc: httpx.HTTPError) -> None:
    """Log a transport-level failure, distinguishing timeout from network."""
    if isinstance(exc, httpx.TimeoutException):
        failure = "timeout"
    else:
        failure = "network"
    logger.warning(
        "[audio] provider=%s operation=%s failure=%s error=%s",
        provider,
        operation,
        failure,
        type(exc).__name__,
    )


def log_audio_config() -> None:
    """Log audio provider configuration status. Call once at startup.

    Never logs the key values — only whether each is configured, plus the
    model/voice the service will use.
    """
    if settings.ELEVENLABS_API_KEY:
        logger.info(
            "[audio-config] ElevenLabs API key configured (model=%s voice_id=%s)",
            settings.ELEVENLABS_MODEL_ID,
            settings.ELEVENLABS_VOICE_ID,
        )
    else:
        logger.error("[audio-config] ERROR: ElevenLabs API key missing — TTS will be unavailable")

    if settings.GROQ_API_KEY:
        logger.info(
            "[audio-config] Groq API key configured (model=%s)",
            settings.GROQ_STT_MODEL,
        )
    else:
        logger.error("[audio-config] ERROR: Groq API key missing — STT will be unavailable")


# ── STT — Groq (OpenAI-compatible Whisper endpoint) ────────────────────────

async def transcribe_audio(audio_bytes: bytes, mime_type: str) -> str:
    """Send browser-recorded audio to Groq Whisper and return the transcript."""
    if not settings.GROQ_API_KEY:
        logger.error("[audio] provider=groq operation=transcribe failure=missing_key")
        raise MissingAudioCredentialsError("Groq API key is not configured.")

    ext = _EXT_MAP.get(mime_type, "webm")
    filename = f"audio.{ext}"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                },
                files={"file": (filename, audio_bytes, mime_type)},
                data={"model": settings.GROQ_STT_MODEL},
            )
    except httpx.TimeoutException as exc:
        _log_transport_error("groq", "transcribe", exc)
        raise AudioServiceError("The transcription service timed out.") from exc
    except httpx.HTTPError as exc:
        _log_transport_error("groq", "transcribe", exc)
        raise AudioServiceError("Could not reach the transcription service.") from exc

    if not response.is_success:
        _log_provider_error(
            "groq",
            "transcribe",
            response,
            model=settings.GROQ_STT_MODEL,
            audio_mime=mime_type,
            audio_bytes=len(audio_bytes),
            key_present=True,
        )
        raise AudioServiceError(f"Groq transcription failed with status {response.status_code}.")

    try:
        result = response.json()
    except ValueError as exc:
        raise AudioServiceError("Invalid JSON response from transcription service.") from exc

    text = (result.get("text") or "").strip()
    if not text:
        raise EmptyTranscriptError("No speech detected in the audio.")
    return text


# ── TTS — ElevenLabs ───────────────────────────────────────────────────────

async def generate_speech(text: str) -> bytes:
    """Convert text to speech via ElevenLabs and return mp3 bytes."""
    if not settings.ELEVENLABS_API_KEY:
        logger.error("[audio] provider=elevenlabs operation=tts failure=missing_key")
        raise MissingAudioCredentialsError("ElevenLabs API key is not configured.")

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": settings.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                json={
                    "text": text,
                    "model_id": settings.ELEVENLABS_MODEL_ID,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
            )
    except httpx.TimeoutException as exc:
        _log_transport_error("elevenlabs", "tts", exc)
        raise AudioServiceError("The speech service timed out.") from exc
    except httpx.HTTPError as exc:
        _log_transport_error("elevenlabs", "tts", exc)
        raise AudioServiceError("Could not reach the speech service.") from exc

    if not response.is_success:
        _log_provider_error(
            "elevenlabs",
            "tts",
            response,
            model=settings.ELEVENLABS_MODEL_ID,
            voice_id=settings.ELEVENLABS_VOICE_ID,
            text_chars=len(text),
            key_present=True,
        )
        raise AudioServiceError(f"ElevenLabs returned status {response.status_code}.")

    audio_bytes = response.content
    if not audio_bytes:
        raise AudioServiceError("ElevenLabs returned empty audio.")
    return audio_bytes

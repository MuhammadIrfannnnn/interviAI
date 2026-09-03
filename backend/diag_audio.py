"""Temporary diagnostic: probe ElevenLabs TTS and Groq STT using the exact
settings the app loads. Prints NO key values and NO partial keys.
Safe to delete after use.
"""
import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from app.core.config import settings
from app.services.audio_service import (
    AudioServiceError,
    EmptyTranscriptError,
    generate_speech,
    transcribe_audio,
)

print("=" * 60)
print("CONFIG (from app settings — no secrets shown)")
print(f"  ELEVENLABS_API_KEY present: {bool(settings.ELEVENLABS_API_KEY)} (len={len(settings.ELEVENLABS_API_KEY)})")
print(f"  GROQ_API_KEY present:       {bool(settings.GROQ_API_KEY)} (len={len(settings.GROQ_API_KEY)})")
print(f"  ELEVENLABS_MODEL_ID: {settings.ELEVENLABS_MODEL_ID}")
print(f"  ELEVENLABS_VOICE_ID: {settings.ELEVENLABS_VOICE_ID}")
print(f"  GROQ_STT_MODEL:      {settings.GROQ_STT_MODEL}")
print("=" * 60)


async def main() -> None:
    # ── Test 1: ElevenLabs TTS ────────────────────────────────────────────
    print("\n[TEST 1] ElevenLabs TTS (via app service)")
    tts_bytes = None
    try:
        tts_bytes = await generate_speech("Hello, welcome to your interview.")
        print(f"  SUCCESS: received {len(tts_bytes)} bytes of audio")
        out = pathlib.Path(__file__).parent / "diag_tts_output.mp3"
        out.write_bytes(tts_bytes)
        print(f"  saved to: {out.name}")
    except AudioServiceError as exc:
        print(f"  FAILED: {exc}")

    # ── Test 2: Groq STT with real speech WAV (if available) ─────────────
    wav_path = pathlib.Path(__file__).parent / "diag_sample.wav"
    print("\n[TEST 2] Groq STT — real speech WAV")
    if wav_path.is_file():
        try:
            text = await transcribe_audio(wav_path.read_bytes(), "audio/wav")
            print(f"  SUCCESS — transcript: {text!r}")
        except EmptyTranscriptError:
            print("  FAILED: provider returned empty transcript")
        except AudioServiceError as exc:
            print(f"  FAILED: {exc}")
    else:
        print(f"  SKIPPED ({wav_path.name} not found)")

    # ── Test 3: Groq STT round-trip with the TTS mp3 (if TTS worked) ────
    print("\n[TEST 3] Groq STT — round-trip of ElevenLabs mp3")
    if tts_bytes:
        try:
            text = await transcribe_audio(tts_bytes, "audio/mpeg")
            print(f"  SUCCESS — transcript: {text!r}")
        except EmptyTranscriptError:
            print("  FAILED: provider returned empty transcript")
        except AudioServiceError as exc:
            print(f"  FAILED: {exc}")
    else:
        print("  SKIPPED (TTS unavailable)")

    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)


asyncio.run(main())

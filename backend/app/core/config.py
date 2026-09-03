from pathlib import Path

from pydantic_settings import BaseSettings,SettingsConfigDict

# backend/ — resolved from this file so .env loads no matter where Uvicorn is started from.
BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    API_PREFIX: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    LLM_PROVIDER:str
    GEMINI_API_KEY:str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    GOOGLE_CLIENT_ID: str
    ELEVENLABS_API_KEY: str = ""   # optional — app still starts without it
    GROQ_API_KEY: str = ""          # optional — app still starts without it

    # Audio providers — optional, with safe defaults.
    # Sarah works via the API on the ElevenLabs FREE plan (Rachel does not —
    # it is a library voice and returns 402 payment_required on free tier).
    ELEVENLABS_VOICE_ID: str = "EXAVITQu4vr4xnSDxMaL"   # Sarah
    ELEVENLABS_MODEL_ID: str = "eleven_turbo_v2_5"
    GROQ_STT_MODEL: str = "whisper-large-v3"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", case_sensitive=True)


settings = Settings()

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.interview import router as interview_router
from app.api.v1.audio import router as audio_router
from app.api.v1.resume import router as resume_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.services.ai_service import GeminiServiceUnavailable
from app.services.audio_service import AudioServiceError, log_audio_config

# Give the app's own loggers a handler so INFO-level status messages are
# visible regardless of the root logger configuration.
_app_logger = logging.getLogger("interviai")
if not _app_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    _app_logger.addHandler(_handler)
    _app_logger.setLevel(logging.INFO)

app=FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def wlcm():
    return {"message":f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
    }
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router,prefix=settings.API_PREFIX)
app.include_router(resume_router,prefix=settings.API_PREFIX)
app.include_router(interview_router,prefix=settings.API_PREFIX)
app.include_router(audio_router, prefix=settings.API_PREFIX)

# Report audio provider configuration at startup (never logs key values).
log_audio_config()

@app.exception_handler(GeminiServiceUnavailable)
async def gemini_service_unavailable_handler(request, exc: GeminiServiceUnavailable):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "The AI interviewer is temporarily unavailable. Please try again in a moment."
        },
    )

@app.exception_handler(AudioServiceError)
async def audio_service_error_handler(request, exc: AudioServiceError):
    return JSONResponse(
        status_code=502,
        content={
            "detail": "Audio service is temporarily unavailable. Please try again."
        },
    )
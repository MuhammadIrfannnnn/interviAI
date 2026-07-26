from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.resume import router as resume_router
from app.api.v1.interview import router as interview_router
from fastapi.middleware.cors import CORSMiddleware

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
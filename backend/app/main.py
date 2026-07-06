from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.auth import router as auth_router

app=FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


@app.get("/")
def wlcm():
    return {"message":f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
    }
app.include_router(auth_router, prefix=settings.API_PREFIX)
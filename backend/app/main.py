from fastapi import FastAPI

app=FastAPI(
    title="InterviAI",
    version="1.0.0",
    description="An AI-powered platform for interview preparation and practice."
)


@app.get("/")
def wlcm():
    return {"message":"hello world"}
from fastapi import FastAPI
from .routes import battlecards, auth

app = FastAPI(title="Battlecard AI SaaS")

app.include_router(battlecards.router, prefix="/api/battlecards", tags=["battlecards"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok", "message": "Service is running"} 
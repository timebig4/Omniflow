from fastapi import FastAPI

from app.api.webhooks import router as webhooks_router
from app.database import init_db

app = FastAPI(title="Omniflow")

app.include_router(webhooks_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def health():
    return {"status": "ok", "service": "omniflow-api"}

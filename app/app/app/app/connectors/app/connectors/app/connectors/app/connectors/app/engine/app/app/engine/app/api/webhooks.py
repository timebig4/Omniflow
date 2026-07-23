from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.engine.tasks import run_workflow_task
from app.models import TriggerType, Workflow

router = APIRouter()


@router.post("/hooks/{webhook_slug}")
async def ingest_webhook(webhook_slug: str, request: Request, db: Session = Depends(get_db)):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.webhook_slug == webhook_slug, Workflow.trigger_type == TriggerType.webhook)
        .first()
    )
    if workflow is None:
        raise HTTPException(status_code=404, detail="Unknown webhook")
    if not workflow.is_active:
        raise HTTPException(status_code=403, detail="Workflow is paused")

    payload = await request.json() if await request.body() else {}

    # Hand off to the worker so the caller gets an instant response,
    # matching how Zapier's webhook triggers behave.
    run_workflow_task.delay(workflow.id, payload)

    return {"status": "accepted"}
